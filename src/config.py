"""
Configuration, Material Properties, Load Cases, and Analytical Baseline
for the 16 mm Combination Wrench (WR-016-200) & M10x30 Hex Bolt (BOLT-M10-030)
Finite Element Simulation in FEniCSx.

All spatial dimensions are in millimeters (mm), forces in Newtons (N),
moments/torques in N*mm, and stresses/moduli in MPa (N/mm^2).
"""

from dataclasses import dataclass
import math
from typing import Dict, List


@dataclass(frozen=True)
class MaterialProperties:
    """Isotropic linear elastic material properties and yield strength."""
    name: str
    standard: str
    E: float          # Young's modulus [MPa]
    nu: float         # Poisson's ratio [-]
    sigma_y: float    # Nominal yield strength [MPa]
    sigma_u: float    # Nominal ultimate tensile strength [MPa]
    density: float    # Mass density [kg/m^3]

    @property
    def lmbda(self) -> float:
        """First Lame parameter lambda [MPa]."""
        return (self.E * self.nu) / ((1.0 + self.nu) * (1.0 - 2.0 * self.nu))

    @property
    def mu(self) -> float:
        """Second Lame parameter mu / shear modulus G [MPa]."""
        return self.E / (2.0 * (1.0 + self.nu))


@dataclass(frozen=True)
class BoltGeometry:
    """Geometric specifications of the ISO 4017 M10x30 Hexagon Head Screw (BOLT-M10-030)."""
    part_number: str = "BOLT-M10-030"
    standard: str = "ISO 4017 - M10 x 30 - 8.8"
    nominal_diameter_d: float = 10.00      # Major thread diameter d [mm]
    pitch_p: float = 1.50                  # Metric coarse thread pitch p [mm]
    across_flats_s: float = 16.00          # Hex head width across flats s [mm]
    head_height_k: float = 6.40            # Hex head height k [mm]
    shank_length_l: float = 30.00          # Under-head shank length l [mm]
    clamped_length: float = 10.00          # Bottom gripped thread engagement length [mm]
    center_x: float = 14.00                # Coaxial X-center matching wrench ring head [mm]
    center_y: float = 0.00                 # Coaxial Y-center matching wrench ring head [mm]

    @property
    def pitch_diameter_d2(self) -> float:
        """Pitch diameter d_2 = d - 0.6495 * p [mm] (Eq. 1)."""
        return self.nominal_diameter_d - 0.6495 * self.pitch_p

    @property
    def minor_diameter_d3(self) -> float:
        """Minor diameter d_3 = d - 1.2268 * p [mm] (Eq. 2)."""
        return self.nominal_diameter_d - 1.2268 * self.pitch_p

    @property
    def equivalent_stress_diameter_ds(self) -> float:
        """Equivalent stress diameter d_s = (d_2 + d_3) / 2 [mm]."""
        return 0.5 * (self.pitch_diameter_d2 + self.minor_diameter_d3)

    @property
    def tensile_stress_area_As(self) -> float:
        """Nominal tensile stress area A_s = (pi / 4) * d_s^2 [mm^2] (Eq. 3)."""
        return 0.25 * math.pi * (self.equivalent_stress_diameter_ds ** 2)

    @property
    def circumradius_R(self) -> float:
        """Circumscribed radius of the hex head R = s / sqrt(3) [mm]."""
        return self.across_flats_s / math.sqrt(3.0)

    @property
    def polar_section_modulus_Wp(self) -> float:
        """Polar section modulus of the threaded shank W_p = pi * d_s^3 / 16 [mm^3] (Eq. 15)."""
        return (math.pi * (self.equivalent_stress_diameter_ds ** 3)) / 16.0


@dataclass(frozen=True)
class WrenchGeometry:
    """Geometric specifications of the 16 mm Combination Wrench (WR-016-200)."""
    part_number: str = "WR-016-200"
    thickness_t: float = 6.50              # Uniform body thickness t [mm]
    total_length: float = 199.55           # Nominal overall length L_total [mm]
    ring_center_x: float = 14.00           # Six-point ring head center X [mm]
    ring_center_y: float = 0.00            # Six-point ring head center Y [mm]
    ring_outer_radius: float = 14.00       # Ring head outer radius R_ring [mm]
    ring_across_flats: float = 16.10       # Six-point hex opening A/F [mm] (0.10 mm clearance)
    open_center_x: float = 183.00          # Open jaw head center X [mm]
    open_center_y: float = 0.00            # Open jaw head center Y [mm]
    open_outer_radius: float = 17.00       # Open jaw head outer radius R_open [mm]
    open_jaw_width: float = 16.10          # Open jaw width [mm]
    open_jaw_angle_deg: float = 15.0       # Open jaw orientation angle [deg]
    open_root_radius: float = 8.05         # Semicircular jaw root radius [mm]
    shank_width_w: float = 14.00           # Straight shank width w [mm] (Y in [-7, +7] mm)
    shank_neck_x1: float = 37.00           # Ring-to-shank transition X coordinate [mm]
    shank_neck_x2: float = 160.00          # Shank-to-open-head transition X coordinate [mm]
    shoulder_fillet_R: float = 3.00        # Transition fillet radius R at (37, +-7) and (160, +-7) [mm]
    stress_concentration_Kt: float = 1.525 # Mean theoretical stress concentration factor (1.45 - 1.60)

    @property
    def center_to_center_Lcc(self) -> float:
        """Effective moment arm L_cc = x_open - x_ring [mm] (Eq. 6)."""
        return self.open_center_x - self.ring_center_x

    @property
    def neck_moment_arm_Lb(self) -> float:
        """Moment arm from applied hand load (x=183 mm) to critical neck (x=37 mm) [mm] (Eq. 8)."""
        return self.open_center_x - self.shank_neck_x1

    @property
    def area_moment_of_inertia_Iz(self) -> float:
        """Area moment of inertia I_z = t * w^3 / 12 [mm^4] (Eq. 9)."""
        return (self.thickness_t * (self.shank_width_w ** 3)) / 12.0

    @property
    def section_modulus_Wz(self) -> float:
        """Elastic section modulus W_z = t * w^2 / 6 [mm^3] (Eq. 10)."""
        return (self.thickness_t * (self.shank_width_w ** 2)) / 6.0


@dataclass(frozen=True)
class LoadCase:
    """Operating load case definition (Table 2 of Pre-Analysis)."""
    case_id: int
    name: str
    description: str
    torque_Nm: float           # Applied tightening torque T [N*m]
    moment_arm_mm: float = 169.0

    @property
    def torque_Nmm(self) -> float:
        """Applied tightening torque T [N*mm]."""
        return self.torque_Nm * 1000.0

    @property
    def hand_force_N(self) -> float:
        """Perpendicular hand force F_hand = T / L_cc [N] (Eq. 7)."""
        return self.torque_Nmm / self.moment_arm_mm


# ==============================================================================
# Standard Material Definitions (Table 1 of Pre-Analysis)
# ==============================================================================
BOLT_MATERIAL = MaterialProperties(
    name="Carbon Steel Class 8.8",
    standard="ISO 898-1 Property Class 8.8 (Quenched & Tempered)",
    E=210_000.0,
    nu=0.30,
    sigma_y=640.0,
    sigma_u=800.0,
    density=7850.0,
)

WRENCH_MATERIAL = MaterialProperties(
    name="AISI 6150 Cr-V Steel",
    standard="AISI 6150 Chromium-Vanadium Steel (44-48 HRC)",
    E=210_000.0,
    nu=0.30,
    sigma_y=1300.0,
    sigma_u=1550.0,
    density=7850.0,
)

BOLT_GEOM = BoltGeometry()
WRENCH_GEOM = WrenchGeometry()

# ==============================================================================
# Standard Load Cases (Table 2 of Pre-Analysis)
# ==============================================================================
LOAD_CASES: List[LoadCase] = [
    LoadCase(
        case_id=1,
        name="Case 1",
        description="Light tightening (60% rated torque)",
        torque_Nm=30.0,
        moment_arm_mm=WRENCH_GEOM.center_to_center_Lcc,
    ),
    LoadCase(
        case_id=2,
        name="Case 2",
        description="Standard Class 8.8 tightening (70% bolt yield preload)",
        torque_Nm=50.0,
        moment_arm_mm=WRENCH_GEOM.center_to_center_Lcc,
    ),
    LoadCase(
        case_id=3,
        name="Case 3",
        description="Peak overload / Seized bolt breakaway",
        torque_Nm=80.0,
        moment_arm_mm=WRENCH_GEOM.center_to_center_Lcc,
    ),
]

# Physical Marker IDs for Gmsh / FEniCSx Mesh Tags
VOLUME_WRENCH_TAG = 1
VOLUME_BOLT_TAG = 2

FACET_BOLT_FIXED_TAG = 101      # Dirichlet BC (u = 0) on clamped bolt thread bottom/sides
FACET_WRENCH_LOAD_TAG = 102     # Neumann BC (traction t) at open-jaw handle grip zone
FACET_CONTACT_DRIVE_TAG = 103   # Engaged hex flats interface between wrench ring and bolt head


def compute_analytical_verification(load_case: LoadCase) -> Dict[str, float]:
    """
    Evaluate theoretical Mechanics of Materials benchmarks for a given load case
    per Section 2.3 of PRE_ANALYSIS.pdf.
    """
    F = load_case.hand_force_N
    T_Nmm = load_case.torque_Nmm

    # 1. Wrench shank bending at critical neck x = 37 mm (Eqs. 11-14)
    M_b = F * WRENCH_GEOM.neck_moment_arm_Lb
    sigma_nom_wrench = M_b / WRENCH_GEOM.section_modulus_Wz
    sigma_peak_wrench_min = 1.45 * sigma_nom_wrench
    sigma_peak_wrench_max = 1.60 * sigma_nom_wrench
    sigma_peak_wrench_mean = WRENCH_GEOM.stress_concentration_Kt * sigma_nom_wrench

    u_y_shank = (F * (WRENCH_GEOM.neck_moment_arm_Lb ** 3)) / (
        3.0 * WRENCH_MATERIAL.E * WRENCH_GEOM.area_moment_of_inertia_Iz
    )

    # 2. Bolt shank torsion at equivalent stress diameter d_s = 8.60 mm (Eqs. 15-17)
    tau_max_bolt = T_Nmm / BOLT_GEOM.polar_section_modulus_Wp
    sigma_vm_bolt_shank = math.sqrt(3.0) * tau_max_bolt

    # Account for combined torsional compliance of the bolt shank + head rotation
    G_bolt = BOLT_MATERIAL.mu
    J_p_bolt = 0.5 * math.pi * ((0.5 * BOLT_GEOM.equivalent_stress_diameter_ds) ** 4)
    L_free_bolt = BOLT_GEOM.shank_length_l - BOLT_GEOM.clamped_length
    theta_bolt_rad = (T_Nmm * L_free_bolt) / (G_bolt * J_p_bolt)
    u_y_total_theory = u_y_shank + theta_bolt_rad * WRENCH_GEOM.center_to_center_Lcc

    return {
        "F_hand_N": F,
        "T_Nmm": T_Nmm,
        "M_b_Nmm": M_b,
        "sigma_nom_wrench_MPa": sigma_nom_wrench,
        "sigma_peak_wrench_min_MPa": sigma_peak_wrench_min,
        "sigma_peak_wrench_max_MPa": sigma_peak_wrench_max,
        "sigma_peak_wrench_mean_MPa": sigma_peak_wrench_mean,
        "SF_wrench_theory": WRENCH_MATERIAL.sigma_y / sigma_peak_wrench_mean,
        "u_y_shank_mm": u_y_shank,
        "u_y_total_theory_mm": u_y_total_theory,
        "tau_max_bolt_MPa": tau_max_bolt,
        "sigma_vm_bolt_shank_MPa": sigma_vm_bolt_shank,
        "SF_bolt_theory": BOLT_MATERIAL.sigma_y / sigma_vm_bolt_shank,
    }
