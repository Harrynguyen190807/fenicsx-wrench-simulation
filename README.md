# FEniCSx Wrench & Hex Bolt Structural Simulation (FEM Course Project)

Repository for the **Numerical Methods (FEM)** Major Assignment: Structural analysis and finite element simulation of a **16 mm Combination Wrench (`WR-016-200`)** engaging an **ISO 4017 M10×30 Hex Bolt (`BOLT-M10-030`)** using Autodesk Inventor and **FEniCSx**.

📄 **[View Pre-Analysis & Theoretical Background Document (`PRE_ANALYSIS.pdf`)](PRE_ANALYSIS.pdf)**

---

## Visual Overview

| 3D CAD Model Preview (`wrench_16mm.ipt`) | Engineering Drawing Sheet 1 (`WR-016-200`) |
| :---: | :---: |
| ![16mm Combination Wrench 3D Preview](cad/previews/wrench_preview.png) | ![Wrench Engineering Drawing Sheet 1](cad/previews/wrench_sheet-1.png) |

---

## Repository Structure

```text
fenicsx-wrench-simulation/
├── PRE_ANALYSIS.pdf                         # Pre-Analysis, CAD Data Analysis & FEM Theory (English PDF)
├── cad/
│   ├── models/                              # 3D Autodesk Inventor part models (.ipt)
│   │   ├── bolt.ipt                         # ISO 4017 M10x30 Hex Head Screw (Property Class 8.8)
│   │   ├── bolt_original.ipt                # Base M10x30 Hex Bolt geometry backup
│   │   └── wrench_16mm.ipt                  # 16 mm Combination Wrench (AISI 6150 Cr-V Steel)
│   ├── drawings/                            # 2D Engineering Drawings (.idw & exported .pdf)
│   │   ├── bolt_drawing.idw                 # Native Inventor drawing for M10x30 bolt
│   │   ├── bolt_drawing.pdf                 # Exported PDF engineering drawing (BOLT-M10-030)
│   │   ├── wrench_16mm_engineering.idw      # Native Inventor drawing for 16 mm wrench
│   │   └── wrench_16mm_engineering.pdf      # Exported 2-sheet PDF engineering drawing (WR-016-200)
│   ├── previews/                            # Rendered CAD previews & drawing check images (.png)
│   │   ├── wrench_preview.png
│   │   ├── wrench_sheet-1.png
│   │   ├── wrench_sheet-2.png
│   │   ├── wrench_final-2.png
│   │   └── drawing_check.png
│   ├── scripts/                             # PowerShell COM automation scripts for Autodesk Inventor
│   │   ├── build_bolt.ps1                   # Automated parametric generation of bolt.ipt
│   │   ├── build_wrench.ps1                 # Automated parametric generation of wrench_16mm.ipt
│   │   ├── drawing.ps1                      # Bolt engineering drawing automation
│   │   ├── wrench_drawing.ps1               # Wrench engineering drawing automation
│   │   ├── export_wrench.ps1                # High-resolution PDF & bitmap export script
│   │   └── ...                              # Inspection, diagnostic, and refinement utilities
│   └── archive/                             # Draft drawings & Inventor OldVersions backups
├── docs/
│   ├── pre_analysis/
│   │   ├── PRE_ANALYSIS.pdf                 # Pre-simulation analysis & FEM formulation (PDF)
│   │   └── phan_tich_va_co_so_ly_thuyet_FEM.tex # Vietnamese LaTeX source of the pre-analysis report
│   └── guidelines/
│       └── Huong_dan_Do_An_PPS.pdf          # Official course project guidelines & grading rubric
├── mesh/                                    # Gmsh / XDMF meshes & mesh convergence study files
├── src/                                     # FEniCSx (dolfinx) Python simulation & solver scripts
├── results/                                 # ParaView outputs (.xdmf/.vtu), contour plots & graphs
└── report/                                  # Final project report (.docx/.tex) & presentation slides
```

---

## 1. CAD Design Specifications & Material Properties

### Component 1: Hexagon Head Screw (`BOLT-M10-030` / [`bolt.ipt`](cad/models/bolt.ipt))
* **Standard:** ISO 4017 — Metric thread $\text{M10} \times 30$ (full thread, pitch $p = 1.5\text{ mm}$, tolerance class $6g$, RH)
* **Head Dimensions:** Width across flats $s = 16.00\text{ mm}$, head height $k = 6.40\text{ mm}$
* **Shank Dimensions:** Under-head length $l = 30.00\text{ mm}$, thread lead-in chamfer $1 \times 45^\circ$
* **Material:** Quenched & tempered carbon steel, **Property Class 8.8** (ISO 898-1)

### Component 2: 16 mm Combination Wrench (`WR-016-200` / [`wrench_16mm.ipt`](cad/models/wrench_16mm.ipt))
* **Overall Geometry:** Uniform thickness $t = 6.50\text{ mm}$, total length $L_{\text{total}} = 199.55\text{ mm}$, center-to-center moment arm $L_{cc} = 169.00\text{ mm}$, mass $m = 148.7\text{ g}$
* **Six-Point Ring Head:** Centered at $(14, 0)\text{ mm}$, outer radius $R_{\text{ring}} = 14.00\text{ mm}$, across flats $A/F = 16.10^{+0.05}_{-0.00}\text{ mm}$
* **Open Jaw Head:** Centered at $(183, 0)\text{ mm}$, outer radius $R_{\text{open}} = 17.00\text{ mm}$, jaw opening $16.10\text{ mm}$ oriented at $15^\circ$
* **Shank Profile:** Straight width $w = 14.00\text{ mm}$, transition shoulder fillets $R = 3.00\text{ mm}$ at $x = 37\text{ mm}$ and $x = 160\text{ mm}$
* **Material:** Chromium-Vanadium alloy steel **AISI 6150 Cr-V** ($44\text{--}48\text{ HRC}$, $\rho = 7850\text{ kg/m}^3$)

| Component | Material | Young's Modulus $E$ (MPa) | Poisson's Ratio $\nu$ | Yield Strength $\sigma_y$ (MPa) |
| :--- | :--- | :---: | :---: | :---: |
| **Hex Bolt M10×30** | Carbon Steel Class 8.8 (ISO 898-1) | $210,000$ | $0.30$ | $640$ |
| **16 mm Wrench** | AISI 6150 Cr-V Steel (44–48 HRC) | $210,000$ | $0.30$ | $1300$ |

---

## 2. Load Cases & Analytical Baseline (Pre-Analysis Summary)

For an $\text{M10} \times 1.5$ Class 8.8 bolt tightened to $70\%$ of yield ($\sigma_{y,\text{bolt}} = 640\text{ MPa}$), the tensile stress area is $A_s \approx 58.0\text{ mm}^2$, assembly preload is $F_M \approx 25,984\text{ N}$ ($26.0\text{ kN}$), and nominal tightening torque (with nut factor $K = 0.19$) is $T_{\text{nom}} \approx 50\text{ N}\cdot\text{m}$. With an effective moment arm $L_{cc} = 183 - 14 = 169\text{ mm}$:

| Load Case | Operating Condition | Torque $T$ ($\text{N}\cdot\text{m}$) | Torque $T$ ($\text{N}\cdot\text{mm}$) | Applied Hand Force $F_{\text{hand}}$ ($\text{N}$) |
| :---: | :--- | :---: | :---: | :---: |
| **Case 1** | Light tightening ($60\%$ rated torque) | $30.0$ | $30,000$ | $177.5$ |
| **Case 2** | Standard Class 8.8 tightening | $50.0$ | $50,000$ | $295.9$ |
| **Case 3** | Peak overload / Seized bolt breakaway | $80.0$ | $80,000$ | $473.4$ |

### Analytical Reference Values (Load Case 2: $T_2 = 50\text{ N}\cdot\text{m}$)
* **Wrench Neck ($x = 37\text{ mm}$, $L_b = 146\text{ mm}$):**
  * Section properties ($t \times w = 6.5 \times 14.0\text{ mm}$): $I_z \approx 1486.33\text{ mm}^4$, $W_z \approx 212.33\text{ mm}^3$
  * Nominal bending stress: $\sigma_{\text{nom}} \approx 203.46\text{ MPa}$
  * Expected peak local stress ($K_t \approx 1.45\text{--}1.60$ at $R = 3\text{ mm}$ fillet): $\sigma_{\max,\text{theory}} \approx 295\text{--}325\text{ MPa}$
  * Cantilever shank tip deflection contribution: $u_{y,\text{shank}} \approx 0.984\text{ mm}$
* **Bolt Shank ($d_s \approx 8.60\text{ mm}$):**
  * Polar section modulus: $W_p \approx 124.89\text{ mm}^3$
  * Maximum torsional shear stress: $\tau_{\max} \approx 400.35\text{ MPa}$ ($\sigma_{\text{vM, shank}} = \sqrt{3}\tau_{\max} \approx 693.4\text{ MPa}$)
* **Lamé Parameters ($E = 210,000\text{ MPa}, \nu = 0.30$):**
  * $\lambda = 121,153.85\text{ MPa}$, $\mu = G = 80,769.23\text{ MPa}$
