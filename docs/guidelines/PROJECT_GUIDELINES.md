# Course Project Guidelines: Numerical Methods (FEM)

## 1. General Information
* **Team Size:** 5 members
* **Grading Breakdown:**
  * **FEM Simulation (50%):** Structural complexity, high-quality FEM results, mandatory mesh convergence study (4–5 mesh levels), realistic boundary conditions, and accurate post-processing.
  * **Technical Report (25%):** Comprehensive 20–40 page report with clear logic, engineering drawings, mathematical formulation, and figures.
  * **Final Presentation (25%):** Week 19 presentation and Q&A defense.

## 2. Report Structure
1. **Title Page & Declaration of Originality**
2. **Table of Contents, List of Figures, List of Tables, Nomenclature**
3. **Executive Summary / Abstract**
4. **Chapter 1: Introduction** — Practical motivation, specific engineering objectives (peak Von Mises stress, critical locations, safety factor evaluation, deflection assessment), and modeling assumptions (isotropic linear elasticity, static loading).
5. **Chapter 2: Problem Description** — 2D/3D CAD engineering drawings (`BOLT-M10-030` and `WR-016-200`), material properties ($E, \nu, \sigma_y, \rho$ per ISO 898-1 and AISI 6150 standards), geometry simplifications, boundary conditions ($\Gamma_D$ and $\Gamma_N$), and multiple load cases (Cases 1–3).
6. **Chapter 3: Finite Element Simulation Workflow** — Geometry import/generation, subdomain material assignment, boundary condition & traction setup, 3D tetrahedral meshing (`C3D10` / $\mathcal{P}_2$ elements), local refinement at fillets/contact zones, and mandatory **5-level Mesh Convergence Study**.
7. **Chapter 4: Results & Discussion** — Contour plots (Von Mises stress $\sigma_{\text{vM}}$, principal stress $\sigma_1$, total displacement $\|\mathbf{u}\|$), Force–Displacement curve, stress profile along the critical neck path ($x = 37\text{ mm}$), comparison with analytical Mechanics of Materials formulas, Safety Factor evaluation, and design optimization recommendations.
8. **Chapter 5: Conclusions & Future Work** — Summary of findings, linear-elastic modeling limitations, and extensions (nonlinear elastoplasticity, contact friction, fatigue analysis).
9. **References & Appendices**
