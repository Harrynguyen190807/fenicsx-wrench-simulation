# FEniCSx 3D Solid Mechanics Simulation Suite (`src/`)

This directory contains the Python Finite Element implementation for the **16 mm Combination Wrench (`WR-016-200`)** & **ISO 4017 M10×30 Hex Bolt (`BOLT-M10-030`)** structural analysis.

## Modules
* [`config.py`](config.py): Material properties (AISI 6150 Cr-V Steel and ISO 898-1 Property Class 8.8 Carbon Steel), CAD geometry parameters, Load Cases 1–3 ($30\text{ N}\cdot\text{m}$, $50\text{ N}\cdot\text{m}$, $80\text{ N}\cdot\text{m}$), and Mechanics of Materials analytical benchmark equations.
* [`generate_mesh.py`](generate_mesh.py): Parametric 3D tetrahedral mesh generator for the coupled Wrench + Hex Bolt assembly with local refinement at the $R = 3.0\text{ mm}$ neck shoulder fillets, six-point hex socket flats, and bolt shank.
* [`fenicsx_solver.py`](fenicsx_solver.py): 3D Linear Elasticity Variational Solver implementing Equations (18)–(30) of [`PRE_ANALYSIS.pdf`](../PRE_ANALYSIS.pdf) using FEniCSx (`dolfinx`, `ufl`, `petsc4py`, `mpi4py`) with automatic 3D Tetrahedral Galerkin sparse solver support and `.vtu` / `.xdmf` ParaView export.
* [`mesh_convergence.py`](mesh_convergence.py): Automated 5-level Mesh Convergence Study (`Coarse` to `Ultra Fine`, $1,824 \rightarrow 34,524\text{ DOFs}$).
* [`postprocess_plots.py`](postprocess_plots.py): High-resolution contour plot, Force–Displacement, Stress Path, and Mesh Convergence figure generator.
* [`run_simulation.py`](run_simulation.py): End-to-end execution script.

## Running the Simulation
```bash
python src/run_simulation.py
```
