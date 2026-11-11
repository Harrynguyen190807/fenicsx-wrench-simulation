# 3D Tetrahedral Meshes (`mesh/`)

Generated 3D tetrahedral meshes (`.vtu` format, compatible with ParaView and FEniCSx) for the coupled **16 mm Combination Wrench (`WR-016-200`)** and **M10×30 Hex Head Bolt (`BOLT-M10-030`)** assembly across 5 refinement levels:

| Mesh Level | File | Characteristic Size $h$ (mm) | Nodes | Tetrahedral Elements | Total DOFs |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **Level 1 (Coarse)** | `wrench_bolt_assembly_L1.vtu` | $4.50$ | $608$ | $2,148$ | $1,824$ |
| **Level 2 (Medium)** | `wrench_bolt_assembly_L2.vtu` | $3.00$ | $1,537$ | $6,480$ | $4,611$ |
| **Level 3 (Fine)** | `wrench_bolt_assembly_L3.vtu` | $2.10$ | $3,443$ | $15,768$ | $10,329$ |
| **Level 4 (Very Fine)** | `wrench_bolt_assembly_L4.vtu` | $1.50$ | $6,617$ | $31,860$ | $19,851$ |
| **Level 5 (Ultra Fine)** | `wrench_bolt_assembly_L5.vtu` | $1.10$ | $11,508$ | $57,456$ | $34,524$ |

### Physical Tags
* **Volume Tags (`SubdomainTag`):**
  * `1`: 16 mm Combination Wrench (AISI 6150 Cr-V Steel, $z \in [0, 6.50]\text{ mm}$)
  * `2`: ISO 4017 M10×30 Hex Bolt (Carbon Steel Class 8.8, $z \in [-30.0, 6.40]\text{ mm}$)
* **Boundary Facet Tags:**
  * `101`: Clamped Bolt Shank Threads ($\Gamma_D$, $\mathbf{u} = \mathbf{0}$ for $z \le -20.0\text{ mm}$)
  * `102`: Wrench Open-Jaw Handle Grip Zone ($\Gamma_N$, applied perpendicular hand force $F_{\text{hand}}$ at $x \approx 183.0\text{ mm}$)
  * `103`: Engaged Six-Point Hex Socket / Bolt Head Drive Flats Interface
