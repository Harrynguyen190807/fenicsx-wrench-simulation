"""
Main Driver Script for the FEniCSx 16 mm Combination Wrench & M10x30 Hex Bolt
Structural Finite Element Simulation.

Usage:
    python src/run_simulation.py
"""

import csv
from pathlib import Path
from typing import List

from config import (
    BOLT_GEOM,
    WRENCH_GEOM,
    BOLT_MATERIAL,
    WRENCH_MATERIAL,
    LOAD_CASES,
    compute_analytical_verification,
)
from generate_mesh import generate_wrench_bolt_assembly_mesh, export_mesh_to_vtk_xml
from fenicsx_solver import SimulationResult, run_wrench_bolt_simulation
from mesh_convergence import run_mesh_convergence_study
from postprocess_plots import (
    plot_von_mises_contour,
    plot_displacement_contour,
    plot_mesh_convergence,
    plot_load_cases_comparison,
    plot_stress_path_and_load_deflection,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    mesh_dir = repo_root / "mesh"
    results_dir = repo_root / "results"
    paraview_dir = results_dir / "paraview"
    figures_dir = results_dir / "figures"

    mesh_dir.mkdir(parents=True, exist_ok=True)
    paraview_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 84)
    print("  FEniCSx 3D SOLID MECHANICS SIMULATION: 16 mm WRENCH (WR-016-200) & M10x30 BOLT")
    print("=" * 84)
    print(f"  Wrench Material : {WRENCH_MATERIAL.name} (E={WRENCH_MATERIAL.E:,.0f} MPa, nu={WRENCH_MATERIAL.nu:.2f}, sigma_y={WRENCH_MATERIAL.sigma_y:.0f} MPa)")
    print(f"  Bolt Material   : {BOLT_MATERIAL.name} (E={BOLT_MATERIAL.E:,.0f} MPa, nu={BOLT_MATERIAL.nu:.2f}, sigma_y={BOLT_MATERIAL.sigma_y:.0f} MPa)")
    print(f"  Lame Parameters : lambda = {WRENCH_MATERIAL.lmbda:,.2f} MPa, mu = G = {WRENCH_MATERIAL.mu:,.2f} MPa")
    print(f"  Moment Arm L_cc : {WRENCH_GEOM.center_to_center_Lcc:.2f} mm (Ring x={WRENCH_GEOM.ring_center_x:.0f} mm -> Open Head x={WRENCH_GEOM.open_center_x:.0f} mm)")
    print("-" * 84)

    # 1. Generate Fine Production Mesh (Level 4) for the 3 Load Cases
    prod_mesh = generate_wrench_bolt_assembly_mesh(refinement_level=4)
    export_mesh_to_vtk_xml(prod_mesh, mesh_dir / f"{prod_mesh.mesh_name}.vtu")
    print(
        f"[1/4] Generated 3D Assembly Mesh '{prod_mesh.mesh_name}': "
        f"{prod_mesh.nodes.shape[0]:,d} nodes, {prod_mesh.cells.shape[0]:,d} tetrahedra "
        f"(h = {prod_mesh.characteristic_h_mm:.2f} mm)"
    )

    # 2. Solve all 3 Operating Load Cases (30 N*m, 50 N*m, 80 N*m)
    print("[2/4] Solving 3D Linear Elasticity Variational Problem Across Load Cases 1-3...")
    case_results: List[SimulationResult] = []
    summary_rows = []

    for lc in LOAD_CASES:
        res = run_wrench_bolt_simulation(prod_mesh, lc, export_dir=paraview_dir)
        case_results.append(res)
        m = res.summary_metrics
        summary_rows.append(m)
        print(
            f"  -> {lc.name} ({lc.torque_Nm:4.1f} N*m | F_hand={lc.hand_force_N:5.1f} N): "
            f"||u||_max = {m['max_displacement_mm']:.3f} mm | "
            f"Wrench sigma_vM = {m['max_vm_wrench_MPa']:5.1f} MPa (SF={m['safety_factor_wrench']:.2f}) | "
            f"Bolt sigma_vM = {m['max_vm_bolt_MPa']:6.1f} MPa (SF={m['safety_factor_bolt']:.2f})"
        )

    summary_csv = results_dir / "load_cases_summary.csv"
    with summary_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    # 3. Execute Mandatory 5-Level Mesh Convergence Study (Load Case 2: T = 50 N*m)
    print("[3/4] Running 5-Level Mesh Convergence Study (Coarse -> Ultra Fine)...")
    conv_csv = results_dir / "mesh_convergence_study.csv"
    conv_rows = run_mesh_convergence_study(output_csv_path=conv_csv, mesh_export_dir=mesh_dir)
    for r in conv_rows:
        print(
            f"  -> {r['label']:20s}: h={r['h_mm']:4.2f} mm | Elements={r['n_elements']:6,d} | "
            f"DOFs={r['n_dofs']:6,d} | Wrench VM={r['max_vm_wrench_MPa']:6.2f} MPa "
            f"(d={r['delta_wrench_pct']:4.2f}%) | Bolt VM={r['max_vm_bolt_MPa']:6.2f} MPa"
        )

    # 4. Generate High-Resolution Engineering Figures
    print("[4/4] Generating Post-Processing Contour Plots & Convergence Graphs...")
    plot_von_mises_contour(case_results[1], figures_dir / "von_mises_contour_case2.png")
    plot_displacement_contour(case_results[1], figures_dir / "displacement_contour_case2.png")
    plot_mesh_convergence(conv_rows, figures_dir / "mesh_convergence_plot.png")
    plot_load_cases_comparison(case_results, figures_dir / "load_cases_comparison.png")
    plot_stress_path_and_load_deflection(case_results, figures_dir / "stress_path_and_load_deflection.png")

    print("-" * 84)
    print("Simulation & Post-Processing Complete!")
    print(f"  * ParaView 3D VTU files : {paraview_dir}")
    print(f"  * Summary CSV tables    : {summary_csv.name}, {conv_csv.name}")
    print(f"  * Engineering figures   : {figures_dir}")
    print("=" * 84)


if __name__ == "__main__":
    main()
