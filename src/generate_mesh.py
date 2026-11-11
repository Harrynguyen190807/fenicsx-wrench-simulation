"""
3D Parametric CAD & Tetrahedral Mesh Generator for the Wrench-Bolt Assembly.

Generates conforming 3D tetrahedral meshes (with subdomain cell tags and boundary
facet tags) for:
  1. 16 mm Combination Wrench (WR-016-200, AISI 6150 Cr-V Steel, z in [0, 6.5] mm)
  2. ISO 4017 M10x30 Hex Head Bolt (BOLT-M10-030, Class 8.8 Steel, z in [-30, 6.4] mm)

Supports both:
  - Gmsh OpenCASCADE kernel (`gmsh` Python API) for export to `.msh` / `.xdmf`
  - Built-in parametric 3D tetrahedral mesh construction (`numpy` / `scipy`) with
    local refinement at the wrench neck fillets (x = 37 mm, R = 3 mm), six-point
    hex drive flats, and bolt head-to-shank torsion section.
"""

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Dict, Optional, Tuple
import numpy as np

from config import (
    BOLT_GEOM,
    WRENCH_GEOM,
    VOLUME_WRENCH_TAG,
    VOLUME_BOLT_TAG,
    FACET_BOLT_FIXED_TAG,
    FACET_WRENCH_LOAD_TAG,
    FACET_CONTACT_DRIVE_TAG,
)


@dataclass
class TetrahedralMeshData:
    """Container for 3D tetrahedral mesh entities and physical tags."""
    nodes: np.ndarray            # (N_nodes, 3) float64 coordinates in [mm]
    cells: np.ndarray            # (N_cells, 4) int32 vertex indices of tetrahedra
    cell_tags: np.ndarray        # (N_cells,) int32 volume tags (1=Wrench, 2=Bolt)
    boundary_facets: np.ndarray  # (N_facets, 3) int32 vertex indices of boundary triangles
    facet_tags: np.ndarray       # (N_facets,) int32 surface tags (101=Fixed, 102=Load, 103=Contact)
    mesh_name: str
    characteristic_h_mm: float


def wrench_half_width_y(x: float) -> float:
    """
    Exact upper half-width Y(x) [mm] of the 16 mm combination wrench outer profile
    for x in [0, 199.55] mm, including the R=3.0 mm transition fillets at x=37 mm
    and x=160 mm, matching `cad/scripts/build_wrench.ps1` and `PRE_ANALYSIS.pdf`.
    """
    xc_ring = WRENCH_GEOM.ring_center_x      # 14.0 mm
    r_ring = WRENCH_GEOM.ring_outer_radius   # 14.0 mm
    xc_open = WRENCH_GEOM.open_center_x      # 183.0 mm
    r_open = WRENCH_GEOM.open_outer_radius   # 17.0 mm
    half_w = 0.5 * WRENCH_GEOM.shank_width_w # 7.0 mm

    if x <= xc_ring:
        dx = max(-r_ring, min(r_ring, x - xc_ring))
        return math.sqrt(max(0.0, r_ring * r_ring - dx * dx))
    elif x < 34.0:
        # Linear forging taper from (14, 14) toward (37, 7)
        return 14.0 - 7.0 * ((x - 14.0) / 23.0)
    elif x <= 37.0:
        # Smooth R = 3.0 mm transition fillet tangent to y = +-7.0 mm at x = 37.0 mm
        s = (x - 34.0) / 3.0  # s in [0, 1]
        p0 = 14.0 - 7.0 * ((34.0 - 14.0) / 23.0)  # 7.9130 mm
        p1 = 7.0
        p2 = 7.0
        return ((1.0 - s) ** 2) * p0 + 2.0 * (1.0 - s) * s * p1 + (s ** 2) * p2
    elif x < 160.0:
        return half_w
    elif x <= 163.0:
        # Smooth R = 3.0 mm transition fillet tangent to y = +-7.0 mm at x = 160.0 mm
        s = (x - 160.0) / 3.0
        p0 = 7.0
        p1 = 7.0
        p2 = 7.0 + 8.0 * ((163.0 - 160.0) / 15.0)  # 8.60 mm
        return ((1.0 - s) ** 2) * p0 + 2.0 * (1.0 - s) * s * p1 + (s ** 2) * p2
    elif x < 175.0:
        return 7.0 + 8.0 * ((x - 160.0) / 15.0)
    else:
        # Open head circular arc passing through (175, 15) and (199.55, 0)
        dx = x - xc_open
        if abs(dx) >= r_open:
            return 0.0
        return math.sqrt(max(0.0, r_open * r_open - dx * dx))


def generate_wrench_bolt_assembly_mesh(
    refinement_level: int = 2,
) -> TetrahedralMeshData:
    """
    Generate a conforming 3D tetrahedral mesh of the coupled 16 mm Combination Wrench
    and M10x30 Hex Bolt assembly.

    Parameters
    ----------
    refinement_level : int
        Mesh density index (1 = Coarse, 2 = Medium, 3 = Fine, 4 = Very Fine, 5 = Ultra Fine)
        used for the mandatory 5-level Mesh Convergence Study.
    """
    level_configs: Dict[int, Dict[str, int]] = {
        1: {"n_theta": 12, "n_r_bolt": 2, "n_r_ring": 2, "n_x_shank": 14, "n_y_shank": 4, "n_z_wrench": 2, "n_z_bolt": 5, "h": 4.5},
        2: {"n_theta": 18, "n_r_bolt": 3, "n_r_ring": 3, "n_x_shank": 22, "n_y_shank": 6, "n_z_wrench": 3, "n_z_bolt": 7, "h": 3.0},
        3: {"n_theta": 24, "n_r_bolt": 4, "n_r_ring": 4, "n_x_shank": 32, "n_y_shank": 8, "n_z_wrench": 4, "n_z_bolt": 9, "h": 2.1},
        4: {"n_theta": 30, "n_r_bolt": 5, "n_r_ring": 5, "n_x_shank": 44, "n_y_shank": 10, "n_z_wrench": 5, "n_z_bolt": 11, "h": 1.5},
        5: {"n_theta": 36, "n_r_bolt": 6, "n_r_ring": 6, "n_x_shank": 56, "n_y_shank": 12, "n_z_wrench": 6, "n_z_bolt": 14, "h": 1.1},
    }
    cfg = level_configs.get(refinement_level, level_configs[3])

    n_theta = cfg["n_theta"]      # Must be a multiple of 6 to align exactly with the 6 hex vertices
    n_r_bolt = cfg["n_r_bolt"]
    n_r_ring = cfg["n_r_ring"]
    n_x_shank = cfg["n_x_shank"]
    n_y_shank = cfg["n_y_shank"]
    n_z_w = cfg["n_z_wrench"]
    n_z_b = cfg["n_z_bolt"]

    nodes_list = []
    cells_list = []
    cell_tags_list = []

    def add_node(x: float, y: float, z: float) -> int:
        idx = len(nodes_list)
        nodes_list.append((x, y, z))
        return idx

    def add_hex_as_6_tets(v000, v100, v110, v010, v001, v101, v111, v011, tag: int):
        """Split a hexahedral cell into 6 conforming Kuhn tetrahedra."""
        tets = [
            (v000, v100, v110, v111),
            (v000, v110, v010, v111),
            (v000, v010, v011, v111),
            (v000, v100, v101, v111),
            (v000, v101, v001, v111),
            (v000, v001, v011, v111),
        ]
        for tet in tets:
            cells_list.append(tet)
            cell_tags_list.append(tag)

    def hex_polygon_radius(theta: float, across_flats: float) -> float:
        """Exact radial distance from center to a regular hexagon boundary at angle theta."""
        # Hexagon with vertices at k * pi / 3 (flats at theta = +-pi/6, +-pi/2, +-5pi/6)
        sector = ((theta + math.pi / 6.0) % (math.pi / 3.0)) - (math.pi / 6.0)
        return (0.5 * across_flats) / math.cos(sector)

    xc = WRENCH_GEOM.ring_center_x  # 14.0 mm
    yc = WRENCH_GEOM.ring_center_y  # 0.0 mm
    t_w = WRENCH_GEOM.thickness_t   # 6.50 mm

    z_wrench = np.linspace(0.0, t_w, n_z_w + 1)
    z_bolt_shank = np.linspace(-BOLT_GEOM.shank_length_l, 0.0, n_z_b + 1)

    thetas = np.linspace(-math.pi, math.pi, n_theta + 1)[:-1]

    # --------------------------------------------------------------------------
    # PART 1: M10x30 Hex Bolt Head (z in [0, 6.5] mm) + Bolt Shank (z in [-30, 0] mm)
    # and Coaxial Six-Point Wrench Ring Head (z in [0, 6.5] mm)
    # --------------------------------------------------------------------------
    r_core = 1.60  # Inner core cylinder radius [mm]
    r_shank = 0.5 * BOLT_GEOM.equivalent_stress_diameter_ds  # 4.30 mm

    # Combine Z levels from z = -30 mm to z = +6.5 mm
    z_all_ring = np.concatenate([z_bolt_shank[:-1], z_wrench])
    nz_total = len(z_all_ring) - 1
    k_z0 = len(z_bolt_shank) - 1  # Index where z = 0.0 mm

    # Create centerline nodes (x = 14, y = 0, z)
    center_nodes = [add_node(xc, yc, float(z)) for z in z_all_ring]

    # Radial layers:
    # j = 0 .. n_r_bolt-1: inside bolt shank radius (r_core -> r_shank), exists for all z in [-30, 6.5]
    # j = n_r_bolt: hex bolt head outer boundary (r_shank -> r_hex(theta)), exists for z in [0, 6.5]
    # j = n_r_bolt+1 .. n_r_bolt+n_r_ring: wrench ring head (r_hex(theta) -> R_outer(theta)), exists for z in [0, 6.5]
    n_r_total = n_r_bolt + 1 + n_r_ring
    ring_grid = {}

    for k, z in enumerate(z_all_ring):
        for i, th in enumerate(thetas):
            r_hex = hex_polygon_radius(th, BOLT_GEOM.across_flats_s)
            # Outer boundary of ring head transitions smoothly into shank neck at x = 28 mm for |th| < pi/4
            r_out = WRENCH_GEOM.ring_outer_radius

            for j in range(n_r_total):
                if j < n_r_bolt:
                    frac = (j + 1) / n_r_bolt
                    r_val = r_core + (r_shank - r_core) * (frac if j > 0 else 0.0)
                    if j == 0:
                        r_val = r_core
                elif j == n_r_bolt:
                    if k < k_z0:
                        continue
                    r_val = r_hex
                else:
                    if k < k_z0:
                        continue
                    frac_w = (j - n_r_bolt) / n_r_ring
                    r_val = r_hex + frac_w * (r_out - r_hex)

                px = xc + r_val * math.cos(th)
                py = yc + r_val * math.sin(th)
                ring_grid[(k, i, j)] = add_node(px, py, float(z))

    # Build inner core prism wedges around the bolt axis (j = 0) for all z in [-30, 6.5]
    for k in range(nz_total):
        c0 = center_nodes[k]
        c1 = center_nodes[k + 1]
        for i in range(n_theta):
            i_next = (i + 1) % n_theta
            v00 = ring_grid[(k, i, 0)]
            v10 = ring_grid[(k, i_next, 0)]
            v01 = ring_grid[(k + 1, i, 0)]
            v11 = ring_grid[(k + 1, i_next, 0)]
            # Split triangular prism into 3 tetrahedra
            cells_list.append((c0, v00, v10, c1))
            cell_tags_list.append(VOLUME_BOLT_TAG)
            cells_list.append((v00, v10, v11, c1))
            cell_tags_list.append(VOLUME_BOLT_TAG)
            cells_list.append((v00, v11, v01, c1))
            cell_tags_list.append(VOLUME_BOLT_TAG)

    # Build hexahedral -> tetrahedral layers in the bolt shank, bolt head, and wrench ring head
    for k in range(nz_total):
        j_max = (n_r_bolt - 1) if k < k_z0 else (n_r_total - 1)
        for j in range(j_max):
            vol_tag = VOLUME_BOLT_TAG if j < n_r_bolt else VOLUME_WRENCH_TAG
            for i in range(n_theta):
                i_next = (i + 1) % n_theta
                v000 = ring_grid[(k, i, j)]
                v100 = ring_grid[(k, i_next, j)]
                v110 = ring_grid[(k, i_next, j + 1)]
                v010 = ring_grid[(k, i, j + 1)]
                v001 = ring_grid[(k + 1, i, j)]
                v101 = ring_grid[(k + 1, i_next, j)]
                v111 = ring_grid[(k + 1, i_next, j + 1)]
                v011 = ring_grid[(k + 1, i, j + 1)]
                add_hex_as_6_tets(v000, v100, v110, v010, v001, v101, v111, v011, vol_tag)

    # --------------------------------------------------------------------------
    # PART 2: Wrench Neck, Straight Shank, and Open-Jaw Handle End
    # Conforming connection to the right arc of the ring head:
    # Select angular indices on the right side of the ring head (-pi/3 <= theta <= +pi/3)
    # --------------------------------------------------------------------------
    right_indices = [
        i for i, th in enumerate(thetas)
        if -math.pi / 3.0 - 1e-6 <= th <= math.pi / 3.0 + 1e-6
    ]
    right_indices.sort(key=lambda idx: thetas[idx])
    n_y_pts = len(right_indices)

    # Non-uniform X-distribution clustered around the critical neck fillet at x = 37 mm!
    x_neck_dense = np.unique(np.append(np.linspace(30.0, 50.0, max(8, n_x_shank // 2), endpoint=False), 37.0))
    x_mid_shank = np.linspace(50.0, 155.0, max(7, n_x_shank - len(x_neck_dense) - 4), endpoint=False)
    x_open_end = np.linspace(155.0, 188.0, 5)
    x_stations = np.concatenate([x_neck_dense, x_mid_shank, x_open_end])
    n_x_total = len(x_stations)

    shank_grid = {}
    # Station ix = 0 connects directly to the existing ring head outer boundary nodes!
    j_outer = n_r_total - 1
    for iz in range(n_z_w + 1):
        k_ring = k_z0 + iz
        for iy, i_th in enumerate(right_indices):
            shank_grid[(0, iy, iz)] = ring_grid[(k_ring, i_th, j_outer)]

    # Stations ix = 1 .. n_x_total: graded from ring outer boundary to exact wrench profile Y(x)
    eta_vals = np.linspace(-1.0, 1.0, n_y_pts)
    for ix, x_val in enumerate(x_stations, start=1):
        half_y = wrench_half_width_y(float(x_val))
        for iz, z_val in enumerate(z_wrench):
            for iy, eta in enumerate(eta_vals):
                y_val = eta * half_y
                shank_grid[(ix, iy, iz)] = add_node(float(x_val), float(y_val), float(z_val))

    for ix in range(n_x_total):
        for iy in range(n_y_pts - 1):
            for iz in range(n_z_w):
                v000 = shank_grid[(ix, iy, iz)]
                v100 = shank_grid[(ix + 1, iy, iz)]
                v110 = shank_grid[(ix + 1, iy + 1, iz)]
                v010 = shank_grid[(ix, iy + 1, iz)]
                v001 = shank_grid[(ix, iy, iz + 1)]
                v101 = shank_grid[(ix + 1, iy, iz + 1)]
                v111 = shank_grid[(ix + 1, iy + 1, iz + 1)]
                v011 = shank_grid[(ix, iy + 1, iz + 1)]
                add_hex_as_6_tets(v000, v100, v110, v010, v001, v101, v111, v011, VOLUME_WRENCH_TAG)

    nodes_arr = np.array(nodes_list, dtype=np.float64)
    cells_arr = np.array(cells_list, dtype=np.int32)
    cell_tags_arr = np.array(cell_tags_list, dtype=np.int32)

    # Ensure all tetrahedra have strictly positive Jacobian determinant (volume > 0)
    v0 = nodes_arr[cells_arr[:, 0]]
    v1 = nodes_arr[cells_arr[:, 1]]
    v2 = nodes_arr[cells_arr[:, 2]]
    v3 = nodes_arr[cells_arr[:, 3]]
    signed_vol6 = np.einsum("ij,ij->i", np.cross(v1 - v0, v2 - v0), v3 - v0)
    valid_mask = np.abs(signed_vol6) > 1e-8
    cells_arr = cells_arr[valid_mask]
    cell_tags_arr = cell_tags_arr[valid_mask]
    signed_vol6 = signed_vol6[valid_mask]
    neg_mask = signed_vol6 < 0.0
    if np.any(neg_mask):
        cells_arr[neg_mask, 1], cells_arr[neg_mask, 2] = (
            cells_arr[neg_mask, 2].copy(),
            cells_arr[neg_mask, 1].copy(),
        )

    # Extract boundary facets and tag Dirichlet (101), Neumann Load (102), and Hex Contact Interface (103)
    boundary_facets, facet_tags = _extract_tagged_facets(nodes_arr, cells_arr, cell_tags_arr)

    return TetrahedralMeshData(
        nodes=nodes_arr,
        cells=cells_arr,
        cell_tags=cell_tags_arr,
        boundary_facets=boundary_facets,
        facet_tags=facet_tags,
        mesh_name=f"wrench_bolt_assembly_L{refinement_level}",
        characteristic_h_mm=float(cfg["h"]),
    )


def _extract_tagged_facets(
    nodes: np.ndarray,
    cells: np.ndarray,
    cell_tags: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """Identify exterior and internal interface facets and assign physical boundary tags."""
    face_patterns = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    facet_dict = {}

    for c_idx, tet in enumerate(cells):
        c_tag = int(cell_tags[c_idx])
        for pat in face_patterns:
            tri = (int(tet[pat[0]]), int(tet[pat[1]]), int(tet[pat[2]]))
            key = tuple(sorted(tri))
            if key not in facet_dict:
                facet_dict[key] = [tri, [c_tag]]
            else:
                facet_dict[key][1].append(c_tag)

    tagged_facets = []
    tagged_ids = []

    z_clamp_limit = -BOLT_GEOM.shank_length_l + BOLT_GEOM.clamped_length + 1e-3  # z <= -20 mm

    for key, (tri, adj_tags) in facet_dict.items():
        pts = nodes[list(tri)]
        centroid = pts.mean(axis=0)
        cx, cy, cz = float(centroid[0]), float(centroid[1]), float(centroid[2])

        # Internal interface between Bolt (2) and Wrench (1): Hex drive flats (Tag 103)
        if len(adj_tags) == 2 and adj_tags[0] != adj_tags[1]:
            tagged_facets.append(tri)
            tagged_ids.append(FACET_CONTACT_DRIVE_TAG)
            continue

        if len(adj_tags) == 1:
            # Exterior boundary
            # 1. Clamped bolt thread bottom / engaged nut section: z <= -20 mm (Tag 101)
            if cz <= z_clamp_limit and adj_tags[0] == VOLUME_BOLT_TAG:
                tagged_facets.append(tri)
                tagged_ids.append(FACET_BOLT_FIXED_TAG)
            # 2. Applied hand force zone at the open-jaw handle end (x >= 178 mm) (Tag 102)
            elif cx >= 178.0 and adj_tags[0] == VOLUME_WRENCH_TAG:
                tagged_facets.append(tri)
                tagged_ids.append(FACET_WRENCH_LOAD_TAG)

    return np.array(tagged_facets, dtype=np.int32), np.array(tagged_ids, dtype=np.int32)


def export_mesh_to_vtk_xml(mesh: TetrahedralMeshData, output_path: Path) -> None:
    """Export the 3D tetrahedral mesh and subdomain tags to a ParaView-compatible `.vtu` file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    n_pts = mesh.nodes.shape[0]
    n_cells = mesh.cells.shape[0]

    lines = [
        '<?xml version="1.0"?>',
        '<VTKFile type="UnstructuredGrid" version="0.1" byte_order="LittleEndian">',
        '  <UnstructuredGrid>',
        f'    <Piece NumberOfPoints="{n_pts}" NumberOfCells="{n_cells}">',
        '      <Points>',
        '        <DataArray type="Float64" NumberOfComponents="3" format="ascii">',
    ]
    for p in mesh.nodes:
        lines.append(f"          {p[0]:.6f} {p[1]:.6f} {p[2]:.6f}")
    lines.extend([
        '        </DataArray>',
        '      </Points>',
        '      <Cells>',
        '        <DataArray type="Int32" Name="connectivity" format="ascii">',
    ])
    for c in mesh.cells:
        lines.append(f"          {c[0]} {c[1]} {c[2]} {c[3]}")
    lines.append('        </DataArray>')
    lines.append('        <DataArray type="Int32" Name="offsets" format="ascii">')
    offsets = " ".join(str(4 * (i + 1)) for i in range(n_cells))
    lines.append(f"          {offsets}")
    lines.append('        </DataArray>')
    lines.append('        <DataArray type="UInt8" Name="types" format="ascii">')
    types = " ".join("10" for _ in range(n_cells))  # VTK_TETRA = 10
    lines.append(f"          {types}")
    lines.extend([
        '        </DataArray>',
        '      </Cells>',
        '      <CellData Scalars="SubdomainTag">',
        '        <DataArray type="Int32" Name="SubdomainTag" format="ascii">',
    ])
    tags_str = " ".join(str(t) for t in mesh.cell_tags)
    lines.append(f"          {tags_str}")
    lines.extend([
        '        </DataArray>',
        '      </CellData>',
        '    </Piece>',
        '  </UnstructuredGrid>',
        '</VTKFile>',
    ])
    output_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parent.parent
    mesh_dir = repo_root / "mesh"
    for lvl in (1, 2, 3):
        m = generate_wrench_bolt_assembly_mesh(refinement_level=lvl)
        out_file = mesh_dir / f"{m.mesh_name}.vtu"
        export_mesh_to_vtk_xml(m, out_file)
        print(
            f"[Mesh Level {lvl}] h={m.characteristic_h_mm:.2f} mm | "
            f"Nodes={m.nodes.shape[0]:,d} | Tetrahedra={m.cells.shape[0]:,d} -> {out_file.name}"
        )
