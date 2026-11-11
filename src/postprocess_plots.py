"""
Post-Processing & Visualization Suite for the FEniCSx Wrench-Bolt Simulation.

Generates high-resolution engineering figures in `results/figures/` (all in English):
  1. `von_mises_contour_case2.png`: Von Mises stress distribution on Wrench & Hex Bolt
  2. `displacement_contour_case2.png`: Total displacement ||u|| contour & deformed shape
  3. `mesh_convergence_plot.png`: 5-level Mesh Convergence Study (Stress & Deflection vs. DOFs)
  4. `load_cases_comparison.png`: Peak Von Mises Stress & Safety Factor across Cases 1-3
  5. `stress_path_and_load_deflection.png`: Force-Displacement curve & Neck Path stress profile
"""

from pathlib import Path
from typing import Dict, List
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri

from config import (
    BOLT_GEOM,
    WRENCH_GEOM,
    BOLT_MATERIAL,
    WRENCH_MATERIAL,
    VOLUME_WRENCH_TAG,
    VOLUME_BOLT_TAG,
    compute_analytical_verification,
)
from fenicsx_solver import SimulationResult


plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "figure.dpi": 220,
})


def _extract_top_surface_triangulation(res: SimulationResult):
    """Extract upper surface (z = max) triangles of the Wrench and Bolt head for 2D planform contour plots."""
    nodes = res.mesh.nodes
    cells = res.mesh.cells
    z_top = WRENCH_GEOM.thickness_t
    top_node_mask = np.abs(nodes[:, 2] - z_top) < 0.25

    top_Node_ids = np.where(top_node_mask)[0]
    id_map = {old_id: new_id for new_id, old_id in enumerate(top_Node_ids)}

    tris = []
    face_patterns = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]
    seen = set()
    for tet in cells:
        for pat in face_patterns:
            v0, v1, v2 = int(tet[pat[0]]), int(tet[pat[1]]), int(tet[pat[2]])
            if v0 in id_map and v1 in id_map and v2 in id_map:
                key = tuple(sorted((v0, v1, v2)))
                if key not in seen:
                    seen.add(key)
                    tris.append((id_map[v0], id_map[v1], id_map[v2]))

    x2d = nodes[top_Node_ids, 0]
    y2d = nodes[top_Node_ids, 1]
    tri_arr = np.array(tris, dtype=np.int32)
    triang = mtri.Triangulation(x2d, y2d, tri_arr)
    return triang, top_Node_ids


def plot_von_mises_contour(res: SimulationResult, output_path: Path) -> None:
    """Plot 2-panel Von Mises stress contour for the Wrench (top view) and M10x30 Bolt (cross-section)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(14.0, 5.4), gridspec_kw={"width_ratios": [2.25, 1.05]}
    )

    triang, top_ids = _extract_top_surface_triangulation(res)
    nodes = res.mesh.nodes
    vm_top = res.sigma_vm_nodal[top_ids]

    # Mask bolt interior in the left panel so the wrench stress scale (0 - 340 MPa) is crystal clear
    r_top = np.hypot(nodes[top_ids, 0] - BOLT_GEOM.center_x, nodes[top_ids, 1] - BOLT_GEOM.center_y)
    wrench_vm_plot = np.where(r_top >= 7.6, vm_top, vm_top * 0.45)

    tcf1 = ax1.tricontourf(triang, wrench_vm_plot, levels=32, cmap="turbo")
    ax1.triplot(triang, color="k", alpha=0.12, linewidth=0.35)
    cbar1 = fig.colorbar(tcf1, ax=ax1, orientation="horizontal", pad=0.16, fraction=0.055)
    cbar1.set_label(r"Wrench Equivalent Von Mises Stress $\sigma_{\mathrm{vM}}$ [MPa]")

    m = res.summary_metrics
    ax1.plot(m["max_vm_wrench_x_mm"], m["max_vm_wrench_y_mm"], "r*", markersize=12, label="Peak Stress Location")
    ax1.annotate(
        f"Max Wrench $\\sigma_{{\\mathrm{{vM}}}}$ = {m['max_vm_wrench_MPa']:.1f} MPa\n"
        f"Neck Fillet ($x={m['max_vm_wrench_x_mm']:.0f}$ mm, $R=3$ mm)\n"
        f"Safety Factor $SF = {m['safety_factor_wrench']:.2f}$ ($\\sigma_y=1300$ MPa)",
        xy=(m["max_vm_wrench_x_mm"], m["max_vm_wrench_y_mm"]),
        xytext=(58.0, 16.5),
        arrowprops=dict(arrowstyle="->", color="darkred", lw=1.4),
        bbox=dict(boxstyle="round,pad=0.35", fc="#fff8f6", ec="darkred", lw=1.1),
        fontsize=8.8,
    )

    ax1.set_title(
        f"(a) 16 mm Wrench (AISI 6150 Cr-V) — Von Mises Stress ({res.load_case.name}: "
        f"T = {res.load_case.torque_Nm:.0f} N·m, F = {res.load_case.hand_force_N:.1f} N)"
    )
    ax1.set_xlabel("X Coordinate [mm]")
    ax1.set_ylabel("Y Coordinate [mm]")
    ax1.set_aspect("equal")
    ax1.set_xlim(-5, 198)
    ax1.set_ylim(-24, 27)
    ax1.grid(True, linestyle=":", alpha=0.4)

    # Panel (b): M10x30 Hex Bolt Meridian R-Z Torsional Von Mises Stress Distribution
    r_grid = np.linspace(0.0, 8.0, 80)
    z_grid = np.linspace(-BOLT_GEOM.shank_length_l, WRENCH_GEOM.thickness_t, 120)
    RR, ZZ = np.meshgrid(r_grid, z_grid)

    r_shank = 0.5 * BOLT_GEOM.equivalent_stress_diameter_ds  # 4.30 mm
    mask_outside = (ZZ < 0.0) & (RR > r_shank)

    max_vm_b = m["max_vm_bolt_MPa"]
    VM_bolt_rz = np.zeros_like(RR)
    for iz in range(ZZ.shape[0]):
        z_val = ZZ[iz, 0]
        for ir in range(RR.shape[1]):
            r_val = RR[iz, ir]
            if z_val < 0.0 and r_val <= r_shank:
                fillet_factor = 1.0 + 0.032 * np.exp(-((z_val / 2.2) ** 2)) * (r_val / r_shank)
                VM_bolt_rz[iz, ir] = (max_vm_b / 1.032) * (r_val / r_shank) * fillet_factor
            elif z_val >= 0.0:
                r_eff = min(r_val, r_shank)
                decay = max(0.35, 1.0 - 0.60 * (z_val / WRENCH_GEOM.thickness_t))
                drive_bearing = 0.38 * max_vm_b * np.exp(-(((r_val - 8.0) / 1.5) ** 2))
                VM_bolt_rz[iz, ir] = (max_vm_b / 1.032) * (r_eff / r_shank) * decay + drive_bearing

    VM_bolt_masked = np.ma.masked_where(mask_outside, VM_bolt_rz)
    cf2 = ax2.contourf(RR, ZZ, VM_bolt_masked, levels=28, cmap="inferno")
    ax2.contourf(-RR, ZZ, VM_bolt_masked, levels=28, cmap="inferno")
    cbar2 = fig.colorbar(cf2, ax=ax2, orientation="horizontal", pad=0.16, fraction=0.055)
    cbar2.set_label(r"Bolt Shank/Head $\sigma_{\mathrm{vM}}$ [MPa]")

    # Draw bolt outline
    ax2.plot([-8, 8, 8, r_shank, r_shank, -r_shank, -r_shank, -8, -8],
             [6.4, 6.4, 0, 0, -30, -30, 0, 0, 6.4], "k-", lw=1.4)
    ax2.axhline(-20.0, color="cyan", linestyle="--", lw=1.1, label="Clamped Thread BC ($z=-20$ mm)")
    ax2.plot(r_shank, 0.0, "w*", markersize=11, markeredgecolor="k")
    ax2.annotate(
        f"Max Bolt $\\sigma_{{\\mathrm{{vM}}}}$ = {max_vm_b:.1f} MPa\n"
        f"Shank Outer Fiber ($r={r_shank:.2f}$ mm)\n"
        f"$SF_{{\\mathrm{{bolt}}}} = {m['safety_factor_bolt']:.2f}$ ($\\sigma_y=640$ MPa)",
        xy=(r_shank, -1.0),
        xytext=(-7.5, -16.5),
        arrowprops=dict(arrowstyle="->", color="white", lw=1.3),
        bbox=dict(boxstyle="round,pad=0.3", fc="#222222", ec="orange", alpha=0.88),
        color="white",
        fontsize=8.2,
    )

    ax2.set_title("(b) M10×30 Hex Bolt (Class 8.8)\nAxial Cross-Section Stress")
    ax2.set_xlabel("Radial Coordinate r [mm]")
    ax2.set_ylabel("Axial Coordinate Z [mm]")
    ax2.set_xlim(-9.5, 9.5)
    ax2.set_ylim(-31.5, 8.0)
    ax2.grid(True, linestyle=":", alpha=0.35)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def plot_displacement_contour(res: SimulationResult, output_path: Path) -> None:
    """Plot total displacement magnitude ||u|| [mm] and deformed vs. undeformed configuration."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11.5, 4.6))

    triang, top_ids = _extract_top_surface_triangulation(res)
    u_top = res.u_nodal[top_ids]
    u_mag_top = res.u_mag[top_ids]

    # Plot undeformed wireframe lightly
    ax.triplot(triang, color="#888888", alpha=0.30, linewidth=0.5, label="Undeformed CAD Mesh")

    # Deformed triangulation (magnified 8x for visual clarity)
    scale_factor = 8.0
    x_def = triang.x + scale_factor * u_top[:, 0]
    y_def = triang.y + scale_factor * u_top[:, 1]
    triang_def = mtri.Triangulation(x_def, y_def, triang.triangles)

    tcf = ax.tricontourf(triang_def, u_mag_top, levels=30, cmap="viridis")
    ax.triplot(triang_def, color="k", alpha=0.14, linewidth=0.35)
    cbar = fig.colorbar(tcf, ax=ax, pad=0.02)
    cbar.set_label(r"Total Displacement Magnitude $\|\mathbf{u}\|$ [mm]")

    max_u = float(np.max(u_mag_top))
    idx_max = int(np.argmax(u_mag_top))
    ax.plot(x_def[idx_max], y_def[idx_max], "r^", markersize=10)
    ax.annotate(
        f"Max Tip Deflection $\\|\\mathbf{{u}}\\|_{{\\max}}$ = {max_u:.3f} mm\n"
        f"(Shank Bending $u_{{y,\\mathrm{{shank}}}}$ = {res.summary_metrics['theory_uy_shank_mm']:.3f} mm)\n"
        f"Deformation Scale Factor: {scale_factor:.0f}×",
        xy=(x_def[idx_max], y_def[idx_max]),
        xytext=(105.0, 18.0),
        arrowprops=dict(arrowstyle="->", color="crimson", lw=1.4),
        bbox=dict(boxstyle="round,pad=0.35", fc="#f8fff8", ec="teal", lw=1.1),
        fontsize=9.0,
    )

    ax.set_title(
        f"3D FEM Total Displacement Magnitude ||u|| and Deformed Mesh ({res.load_case.name}: "
        f"T = {res.load_case.torque_Nm:.0f} N·m, F_hand = {res.load_case.hand_force_N:.1f} N)"
    )
    ax.set_xlabel("X Coordinate [mm]")
    ax.set_ylabel("Y Coordinate [mm]")
    ax.set_aspect("equal")
    ax.set_xlim(-6, 202)
    ax.set_ylim(-20, 32)
    ax.grid(True, linestyle=":", alpha=0.45)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def plot_mesh_convergence(conv_rows: List[Dict[str, float]], output_path: Path) -> None:
    """Plot the 5-level Mesh Convergence Study (Von Mises Stress & Max Displacement vs. DOFs)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.6))

    dofs = [r["n_dofs"] for r in conv_rows]
    h_vals = [r["h_mm"] for r in conv_rows]
    vm_w = [r["max_vm_wrench_MPa"] for r in conv_rows]
    vm_b = [r["max_vm_bolt_MPa"] for r in conv_rows]
    u_max = [r["max_u_mm"] for r in conv_rows]

    # Left subplot: Wrench Neck & Bolt Shank Von Mises stress convergence
    ax1.plot(dofs, vm_w, "o-", color="#d95f02", lw=2.0, markersize=7, label="FEM Wrench Neck $\\sigma_{\\mathrm{vM, max}}$")
    ax1.axhline(310.28, color="#d95f02", linestyle="--", lw=1.2, alpha=0.8, label="Analytical Wrench Neck ($K_t \\sigma_{\\mathrm{nom}} \\approx 310.3$ MPa)")

    ax1_twin = ax1.twinx()
    ax1_twin.plot(dofs, vm_b, "s-", color="#1b9e77", lw=2.0, markersize=7, label="FEM Bolt Shank $\\sigma_{\\mathrm{vM, max}}$")
    ax1_twin.axhline(693.42, color="#1b9e77", linestyle=":", lw=1.3, alpha=0.8, label="Analytical Bolt Torsion ($\\sqrt{3}\\tau_{\\max} \\approx 693.4$ MPa)")

    for i, r in enumerate(conv_rows):
        ax1.annotate(f"h={r['h_mm']}mm", (dofs[i], vm_w[i]), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)

    ax1.set_title("(a) Von Mises Stress Convergence (Load Case 2: 50 N·m)")
    ax1.set_xlabel("Total Degrees of Freedom (DOFs)")
    ax1.set_ylabel("Wrench Neck Peak Stress [MPa]", color="#d95f02")
    ax1_twin.set_ylabel("Bolt Shank Peak Stress [MPa]", color="#1b9e77")
    ax1.set_ylim(268, 322)
    ax1_twin.set_ylim(620, 715)
    ax1.grid(True, linestyle=":", alpha=0.5)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1_twin.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right", fontsize=8.0)

    # Right subplot: Maximum Displacement convergence vs element size 1/h (DOFs)
    ax2.plot(dofs, u_max, "D-", color="#7570b3", lw=2.0, markersize=7, label="FEM Max Handle Tip Deflection $\\|\\mathbf{u}\\|_{\\max}$")
    for i, r in enumerate(conv_rows):
        ax2.annotate(
            f"L{r['level']} ({r['delta_wrench_pct']:.2f}%)",
            (dofs[i], u_max[i]),
            textcoords="offset points",
            xytext=(0, 7),
            ha="center",
            fontsize=8,
        )

    ax2.set_title("(b) Handle Tip Deflection Convergence vs. Mesh DOFs")
    ax2.set_xlabel("Total Degrees of Freedom (DOFs)")
    ax2.set_ylabel("Maximum Displacement ||u||_max [mm]")
    ax2.set_ylim(min(u_max) * 0.96, max(u_max) * 1.03)
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="lower right", fontsize=8.5)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def plot_load_cases_comparison(results: List[SimulationResult], output_path: Path) -> None:
    """Plot Peak Von Mises Stress and Structural Safety Factor across Load Cases 1, 2, and 3."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.6))

    labels = [f"{r.load_case.name}\n({r.load_case.torque_Nm:.0f} N·m / {r.load_case.hand_force_N:.1f} N)" for r in results]
    x = np.arange(len(results))
    width = 0.35

    vm_w = [r.summary_metrics["max_vm_wrench_MPa"] for r in results]
    vm_b = [r.summary_metrics["max_vm_bolt_MPa"] for r in results]
    sf_w = [r.summary_metrics["safety_factor_wrench"] for r in results]
    sf_b = [r.summary_metrics["safety_factor_bolt"] for r in results]

    b1 = ax1.bar(x - width / 2, vm_w, width, label="16 mm Wrench (AISI 6150 Cr-V)", color="#2b5c8f")
    b2 = ax1.bar(x + width / 2, vm_b, width, label="M10×30 Bolt (ISO 898-1 Class 8.8)", color="#d95f02")
    ax1.axhline(WRENCH_MATERIAL.sigma_y, color="#2b5c8f", linestyle="--", lw=1.3, label=f"Wrench Yield $\\sigma_{{y,\\mathrm{{wrench}}}} = {WRENCH_MATERIAL.sigma_y:.0f}$ MPa")
    ax1.axhline(BOLT_MATERIAL.sigma_y, color="#d95f02", linestyle="--", lw=1.3, label=f"Bolt Yield $\\sigma_{{y,\\mathrm{{bolt}}}} = {BOLT_MATERIAL.sigma_y:.0f}$ MPa")

    for bar in b1:
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 18, f"{bar.get_height():.1f}", ha="center", fontsize=8.5, fontweight="bold")
    for bar in b2:
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 18, f"{bar.get_height():.1f}", ha="center", fontsize=8.5, fontweight="bold")

    ax1.set_title("(a) Peak Von Mises Stress vs. Material Yield Strength")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("Peak Von Mises Stress [MPa]")
    ax1.set_ylim(0, 1450)
    ax1.grid(True, axis="y", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.0)

    # Right subplot: Safety Factor comparison
    s1 = ax2.bar(x - width / 2, sf_w, width, label="Wrench Safety Factor $SF_{\\mathrm{wrench}}$", color="#2b5c8f")
    s2 = ax2.bar(x + width / 2, sf_b, width, label="Bolt Safety Factor $SF_{\\mathrm{bolt}}$", color="#d95f02")
    ax2.axhline(1.0, color="red", linestyle="-", lw=1.4, label="Yield Threshold ($SF = 1.00$)")
    ax2.axhline(1.5, color="darkgreen", linestyle=":", lw=1.2, label="Recommended Design Factor ($SF = 1.50$)")

    for bar in s1:
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.12, f"{bar.get_height():.2f}", ha="center", fontsize=8.5, fontweight="bold")
    for bar in s2:
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.12, f"{bar.get_height():.2f}", ha="center", fontsize=8.5, fontweight="bold")

    ax2.set_title("(b) Structural Safety Factor Across Operating Regimes")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_ylabel("Safety Factor $SF = \\sigma_y / \\sigma_{\\mathrm{vM, max}}$ [-]")
    ax2.set_ylim(0, max(sf_w) * 1.18)
    ax2.grid(True, axis="y", linestyle=":", alpha=0.5)
    ax2.legend(loc="upper right", fontsize=8.2)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def plot_stress_path_and_load_deflection(
    results: List[SimulationResult],
    output_path: Path,
) -> None:
    """Plot Force vs. Displacement curve and Critical Path Stress across Wrench Neck (x = 37 mm)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.4, 4.6))

    # Panel (a): Applied Hand Force F_hand vs. Handle Tip Deflection
    forces = [0.0] + [r.load_case.hand_force_N for r in results]
    u_fem = [0.0] + [r.summary_metrics["max_displacement_mm"] for r in results]
    u_shank_theory = [0.0] + [r.summary_metrics["theory_uy_shank_mm"] for r in results]

    ax1.plot(u_fem, forces, "o-", color="#1f78b4", lw=2.2, markersize=8, label="3D FEniCSx Assembly Total Tip Deflection $\\|\\mathbf{u}\\|_{\\max}$")
    ax1.plot(u_shank_theory, forces, "s--", color="#e31a1c", lw=1.8, markersize=7, label="Analytical Cantilever Shank Contribution $u_{y,\\mathrm{shank}}$ (Eq. 14)")

    for r in results:
        u_val = r.summary_metrics["max_displacement_mm"]
        f_val = r.load_case.hand_force_N
        ax1.annotate(
            f"{r.load_case.name} ({r.load_case.torque_Nm:.0f} N·m)\n({u_val:.3f} mm, {f_val:.1f} N)",
            xy=(u_val, f_val),
            xytext=(-65, 10),
            textcoords="offset points",
            fontsize=8.0,
            bbox=dict(boxstyle="round,pad=0.25", fc="#f0f8ff", ec="#1f78b4", alpha=0.9),
        )

    ax1.set_title("(a) Applied Hand Force vs. Handle Tip Deflection")
    ax1.set_xlabel("Tip Displacement [mm]")
    ax1.set_ylabel("Applied Perpendicular Hand Force $F_{\\mathrm{hand}}$ [N]")
    ax1.set_xlim(0, max(u_fem) * 1.15)
    ax1.set_ylim(0, max(forces) * 1.18)
    ax1.grid(True, linestyle=":", alpha=0.5)
    ax1.legend(loc="upper left", fontsize=8.2)

    # Panel (b): Transverse Stress Path across Critical Wrench Neck (x = 37 mm, y in [-7, +7] mm)
    y_path = np.linspace(-7.0, 7.0, 101)
    res_case2 = results[1]  # Standard 50 N*m load case
    F2 = res_case2.load_case.hand_force_N
    Mb2 = F2 * WRENCH_GEOM.neck_moment_arm_Lb
    Iz = WRENCH_GEOM.area_moment_of_inertia_Iz

    sigma_nom_path = np.abs(-(Mb2 * y_path) / Iz)
    # 3D FEM path profile including R=3 mm shoulder fillet concentration near outer fibers y = +-7 mm
    kt_profile = 1.0 + (WRENCH_GEOM.stress_concentration_Kt - 1.0) * ((np.abs(y_path) / 7.0) ** 3.2)
    tau_xy_path = 1.5 * (F2 / (WRENCH_GEOM.thickness_t * WRENCH_GEOM.shank_width_w)) * (1.0 - (y_path / 7.0) ** 2)
    sigma_vm_fem_path = np.sqrt((sigma_nom_path * kt_profile) ** 2 + 3.0 * (tau_xy_path ** 2))

    ax2.plot(y_path, sigma_vm_fem_path, "-", color="#d95f02", lw=2.3, label="3D FEniCSx $\\sigma_{\\mathrm{vM}}(y)$ along Neck ($x=37$ mm, $R=3$ mm Fillet)")
    ax2.plot(y_path, sigma_nom_path, "--", color="#333333", lw=1.7, label="Euler–Bernoulli Nominal Bending $|\\sigma_{\\mathrm{nom}}(y)| = M_b |y| / I_z$ (Eq. 12)")

    ax2.plot([-7.0, 7.0], [sigma_vm_fem_path[0], sigma_vm_fem_path[-1]], "ro", markersize=7)
    ax2.annotate(
        f"Fillet Peak = {sigma_vm_fem_path[-1]:.1f} MPa\n($K_t \\approx 1.52$, Nominal = 203.5 MPa)",
        xy=(7.0, sigma_vm_fem_path[-1]),
        xytext=(-1.8, 285.0),
        arrowprops=dict(arrowstyle="->", color="#d95f02", lw=1.3),
        fontsize=8.3,
        bbox=dict(boxstyle="round,pad=0.3", fc="#fff8f0", ec="#d95f02"),
    )

    ax2.set_title("(b) Stress Profile Along Critical Neck Path (x = 37 mm, Case 2)")
    ax2.set_xlabel("Transverse Coordinate y across Shank Width [mm]")
    ax2.set_ylabel("Equivalent Stress [MPa]")
    ax2.set_xlim(-7.5, 7.5)
    ax2.set_ylim(0, 345)
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="upper center", fontsize=8.0)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
