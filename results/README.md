# FEniCSx Simulation Results & Post-Processing (`results/`)

## Contents
* [`load_cases_summary.csv`](load_cases_summary.csv): Quantitative FEM simulation results and analytical comparisons across Load Cases 1, 2, and 3 ($30\text{ N}\cdot\text{m}$, $50\text{ N}\cdot\text{m}$, $80\text{ N}\cdot\text{m}$).
* [`mesh_convergence_study.csv`](mesh_convergence_study.csv): Tabulated 5-level Mesh Convergence Study results ($h = 4.50\text{ mm} \rightarrow 1.10\text{ mm}$).
* `paraview/`: Full 3D unstructured grid solution files (`.vtu`) containing `Displacement_mm`, `VonMises_MPa`, `MaxPrincipal_S1_MPa`, `Sigma_xx_MPa`, `Tau_xy_MPa`, and `SafetyFactor` fields for interactive 3D exploration in ParaView:
  * `solution_case1_case_1.vtu` ($T_1 = 30.0\text{ N}\cdot\text{m}$, $F_{\text{hand}} = 177.5\text{ N}$)
  * `solution_case2_case_2.vtu` ($T_2 = 50.0\text{ N}\cdot\text{m}$, $F_{\text{hand}} = 295.9\text{ N}$)
  * `solution_case3_case_3.vtu` ($T_3 = 80.0\text{ N}\cdot\text{m}$, $F_{\text{hand}} = 473.4\text{ N}$)
* `figures/`: High-resolution engineering plots:
  * [`von_mises_contour_case2.png`](figures/von_mises_contour_case2.png)
  * [`displacement_contour_case2.png`](figures/displacement_contour_case2.png)
  * [`mesh_convergence_plot.png`](figures/mesh_convergence_plot.png)
  * [`load_cases_comparison.png`](figures/load_cases_comparison.png)
  * [`stress_path_and_load_deflection.png`](figures/stress_path_and_load_deflection.png)
