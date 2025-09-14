# def get_flow_regime(Re: float) -> str:
# def calculate_flow_parameters(
# def nusselt_number(reynolds_number: float, prandtl_number: float, flow_regime: str) -> float:
# def pressure_drop(
# def convective_heat_transfer(
import math

def flow_regime_from_re(reynolds_number: float) -> str:
    """Returnerer strømningsregime basert på Reynolds-tall."""
    if reynolds_number < 2300:
        return "Laminær"
    elif 2300 <= reynolds_number <= 4000:
        return "Overgangsstrømning"
    else:
        return "Turbulent"

def reynolds_number(mass_flow_rate: float, density: float, dynamic_viscosity: float, hydraulic_diameter: float, flow_area: float) -> float:
    """Returnerer Reynolds-tallet."""
    velocity = mass_flow_rate / (density * flow_area)
    return density * velocity * hydraulic_diameter / dynamic_viscosity

def prandtl_number(specific_heat_capacity: float, dynamic_viscosity: float, thermal_conductivity: float) -> float:
    """Returnerer Prandtl-tallet."""
    return specific_heat_capacity * dynamic_viscosity / thermal_conductivity

def nusselt_number(reynolds: float, prandtl: float, flow_regime: str) -> float:
    """Returnerer Nusselt-tallet."""
    if flow_regime == "Laminær":
        nusselt = 7.54
    elif flow_regime == "Overgangsstrømning":
        nusselt_laminar = 7.54
        friction_factor = (0.79 * math.log(reynolds) - 1.64)**-2 if reynolds > 2300 else 96/reynolds
        nusselt_turbulent = (
            (friction_factor/8) * (reynolds - 1000) * prandtl /
            (1 + 12.7 * math.sqrt(friction_factor/8) * (prandtl**(2/3) - 1))
        )
        weight = (reynolds - 2300) / (4000 - 2300)
        nusselt = nusselt_laminar + weight * (nusselt_turbulent - nusselt_laminar)
    else:
        friction_factor = (0.79 * math.log(reynolds) - 1.64)**-2
        nusselt = (
            (friction_factor/8) * (reynolds - 1000) * prandtl /
            (1 + 12.7 * math.sqrt(friction_factor/8) * (prandtl**(2/3) - 1))
        )
    return nusselt

def friction_factor(reynolds: float, flow_regime: str) -> float:
    """Returnerer friksjonsfaktor."""
    if flow_regime == "Laminær":
        return 96 / reynolds
    elif flow_regime == "Overgangsstrømning":
        f_laminar = 96 / reynolds
        f_turbulent = (0.79 * math.log(reynolds) - 1.64)**-2
        weight = (reynolds - 2300) / (4000 - 2300)
        return f_laminar + weight * (f_turbulent - f_laminar)
    else:
        return (0.79 * math.log(reynolds) - 1.64)**-2

def velocity(mass_flow_rate: float, density: float, flow_area: float) -> float:
    """Returnerer lufthastighet."""
    return mass_flow_rate / (density * flow_area)

def pressure_drop(friction_factor: float, length: float, hydraulic_diameter: float, density: float, velocity: float) -> float:
    """Returnerer trykkfall i kanalen."""
    return friction_factor * (length / hydraulic_diameter) * (density * velocity**2) / 2

def flow_side_results(
    mass_flow_rate: float,
    density: float,
    dynamic_viscosity: float,
    specific_heat_capacity: float,
    thermal_conductivity: float,
    flow_area: float,
    hydraulic_diameter: float,
    length: float
) -> dict:
    """Samler alle relevante strømningstall for én side og returnerer som dict."""
    re = reynolds_number(mass_flow_rate, density, dynamic_viscosity, hydraulic_diameter, flow_area)
    regime = flow_regime_from_re(re)
    pr = prandtl_number(specific_heat_capacity, dynamic_viscosity, thermal_conductivity)
    nu = nusselt_number(re, pr, regime)
    vel = velocity(mass_flow_rate, density, flow_area)
    h = nu * thermal_conductivity / hydraulic_diameter
    f = friction_factor(re, regime)
    dp = pressure_drop(f, length, hydraulic_diameter, density, vel)
    volumetric_flow_rate = mass_flow_rate / density
    mass_flux = mass_flow_rate / flow_area
    return {
        "reynolds_number": re,
        "flow_regime": regime,
        "prandtl_number": pr,
        "nusselt_number": nu,
        "velocity": vel,
        "heat_transfer_coefficient": h,
        "friction_factor": f,
        "pressure_drop": dp,
        "volumetric_flow_rate": volumetric_flow_rate,
        "mass_flux": mass_flux
    }
