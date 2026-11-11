"""
Mesh Convergence Study for the 16 mm Combination Wrench & M10x30 Hex Bolt Assembly.

Executes 5 progressive 3D tetrahedral mesh refinement levels under the nominal
design load (Load Case 2: T = 50 N*m, F_hand = 295.9 N) to verify spatial
discretization convergence of:
  - Peak Von Mises stress at the wrench neck fillet (x = 37 mm, R = 3 mm)
  - Peak Von Mises stress in the M10x30 bolt shank (d_s = 8.60 mm)
  - Maximum wrench handle tip displacement ||u||_max
"""

import csv
from pathlib import Path
from typing import Dict, List

from config import LOAD_CASES
from generate_mesh import generate_wrench_bolt_assembly_mesh, export_mesh_to_vtk_xml
from fenicsx_solver import run_wrench_bolt_simulation


def run_mesh_convergence_study(
    output_csv_path: Path,
    mesh_export_dir: Path,
) -> List[Dict[str, float]]:
    """
    Run the 5-level mesh convergence study for Load Case 2 (T = 50 N*m) and export
    the convergence metrics to CSV.
    """
    nominal_case = LOAD_CASES[1]  # Case 2: 50.0 N*m (295.9 N)
    records: List[Dict[str, float]] = []

    level_labels = {
        1: "Mesh 1 (Coarse)",
        2: "Mesh 2 (Medium)",
        3: "Mesh 3 (Fine)",
        4: "Mesh 4 (Very Fine)",
        5: "Mesh 5 (Ultra Fine)",
    }

    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    mesh_export_dir.mkdir(parents=True, exist_ok=True)

    for lvl in range(1, 6):
        mesh_data = generate_wrench_bolt_assembly_mesh(refinement_level=lvl)
        export_mesh_to_vtk_xml(mesh_data, mesh_export_dir / f"{mesh_data.mesh_name}.vtu")

        res = run_wrench_bolt_simulation(mesh_data, nominal_case, export_dir=None)
        m = res.summary_metrics

        prev_w = records[-1]["max_vm_wrench_MPa"] if records else None
        prev_b = records[-1]["max_vm_bolt_MPa"] if records else None
        delta_w_pct = (100.0 * abs(m["max_vm_wrench_MPa"] - prev_w) / prev_w) if prev_w else 0.0
        delta_b_pct = (100.0 * abs(m["max_vm_bolt_MPa"] - prev_b) / prev_b) if prev_b else 0.0

        row = {
            "level": lvl,
            "label": level_labels[lvl],
            "h_mm": mesh_data.characteristic_h_mm,
            "n_nodes": int(mesh_data.nodes.shape[0]),
            "n_elements": int(mesh_data.cells.shape[0]),
            "n_dofs": int(res.n_dofs),
            "max_u_mm": m["max_displacement_mm"],
            "shank_uy_mm": m["shank_tip_uy_mm"],
            "max_vm_wrench_MPa": m["max_vm_wrench_MPa"],
            "max_vm_bolt_MPa": m["max_vm_bolt_MPa"],
            "delta_wrench_pct": delta_w_pct,
            "delta_bolt_pct": delta_b_pct,
            "solve_time_s": res.solve_time_s,
        }
        records.append(row)

    fieldnames = list(records[0].keys())
    with output_csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    return records


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    rows = run_mesh_convergence_study(
        output_csv_path=root / "results" / "mesh_convergence_study.csv",
        mesh_export_dir=root / "mesh",
    )
    for r in rows:
        print(
            f"{r['label']:20s} | h={r['h_mm']:4.2f} mm | Elements={r['n_elements']:6,d} | "
            f"DOFs={r['n_dofs']:6,d} | U_max={r['max_u_mm']:.4f} mm | "
            f"sigma_vM(Wrench)={r['max_vm_wrench_MPa']:.2f} MPa | "
            f"sigma_vM(Bolt)={r['max_vm_bolt_MPa']:.2f} MPa"
        )
