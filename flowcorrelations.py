from typing import Optional
import math
from pydantic import BaseModel, Field

# Konstanter for regimegrenser
RE_LAMINAR = 2300
RE_TURBULENT = 4000

class FLowInputModel(BaseModel):
    mass_flow_rate: float = Field(..., title="Masseflow (kg/s)")
    density: float = Field(..., title="Tetthet (kg/m³)")
    dynamic_viscosity: float = Field(..., title="Dynamisk viskositet (Pa·s)")
    specific_heat_capacity: float = Field(..., title="Spesifikk varmekapasitet (J/kgK)")
    thermal_conductivity: float = Field(..., title="Termisk konduktivitet (W/mK)")
    flow_area: float = Field(..., title="Tverrsnittsareal (m²)")
    hydraulic_diameter: float = Field(..., title="Hydraulisk diameter (m)")
    length: float = Field(..., title="Lengde (m)")

class FlowResults(BaseModel):
    reynolds_number: float = Field(..., title="Reynolds-tall")
    flow_regime: str = Field(..., title="Strømningsregime")
    prandtl_number: float = Field(..., title="Prandtl-tall")
    nusselt_number: float = Field(..., title="Nusselt-tall")
    velocity: float = Field(..., title="Hastighet (m/s)")
    heat_transfer_coefficient: float = Field(..., title="Varmeovergangskoeffisient (W/m²K)")
    friction_factor: float = Field(..., title="Friksjonsfaktor")
    pressure_drop: float = Field(..., title="Trykkfall (Pa)")
    volumetric_flow_rate: float = Field(..., title="Volumstrøm (m³/s)")
    mass_flux: float = Field(..., title="Massefluks (kg/m²s)")

def flow_regime_from_re(reynolds_number: float) -> str:
    """Returnerer strømningsregime basert på Reynolds-tall."""
    if reynolds_number < RE_LAMINAR:
        return "Laminær"
    elif RE_LAMINAR <= reynolds_number <= RE_TURBULENT:
        return "Overgangsstrømning"
    else:
        return "Turbulent"

def reynolds_number(mass_flow_rate: float, density: float, dynamic_viscosity: float, hydraulic_diameter: float, flow_area: float) -> float:
    """
    Returnerer Reynolds-tallet.
    mass_flow_rate: Masseflow (kg/s)
    density: Tetthet (kg/m³)
    dynamic_viscosity: Dynamisk viskositet (Pa·s)
    hydraulic_diameter: Hydraulisk diameter (m)
    flow_area: Tverrsnittsareal (m²)
    """
    if density <= 0 or flow_area <= 0 or dynamic_viscosity <= 0 or hydraulic_diameter <= 0:
        return float('nan')
    velocity = mass_flow_rate / (density * flow_area)
    return density * velocity * hydraulic_diameter / dynamic_viscosity

def prandtl_number(specific_heat_capacity: float, dynamic_viscosity: float, thermal_conductivity: float) -> float:
    """
    Returnerer Prandtl-tallet.
    specific_heat_capacity: Spesifikk varmekapasitet (J/kgK)
    dynamic_viscosity: Dynamisk viskositet (Pa·s)
    thermal_conductivity: Termisk konduktivitet (W/mK)
    """
    if thermal_conductivity == 0:
        return float('nan')
    return specific_heat_capacity * dynamic_viscosity / thermal_conductivity

def nusselt_number(reynolds: float, prandtl: float, flow_regime: str) -> float:
    """Returnerer Nusselt-tallet."""
    if flow_regime == "Laminær":
        nusselt = 7.54
    elif flow_regime == "Overgangsstrømning":
        nusselt_laminar = 7.54
        friction_factor = (0.79 * math.log(reynolds) - 1.64)**-2 if reynolds > RE_LAMINAR else 96/reynolds
        nusselt_turbulent = (
            (friction_factor/8) * (reynolds - 1000) * prandtl /
            (1 + 12.7 * math.sqrt(friction_factor/8) * (prandtl**(2/3) - 1))
        )
        weight = (reynolds - RE_LAMINAR) / (RE_TURBULENT - RE_LAMINAR)
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
    if reynolds <= 0:
        return float('nan')
    if flow_regime == "Laminær":
        return 96 / reynolds
    elif flow_regime == "Overgangsstrømning":
        f_laminar = 96 / reynolds
        f_turbulent = (0.79 * math.log(reynolds) - 1.64)**-2
        weight = (reynolds - RE_LAMINAR) / (RE_TURBULENT - RE_LAMINAR)
        return f_laminar + weight * (f_turbulent - f_laminar)
    else:
        return (0.79 * math.log(reynolds) - 1.64)**-2

def velocity(mass_flow_rate: float, density: float, flow_area: float) -> float:
    """
    Returnerer lufthastighet.
    mass_flow_rate: Masseflow (kg/s)
    density: Tetthet (kg/m³)
    flow_area: Tverrsnittsareal (m²)
    """
    if density <= 0 or flow_area <= 0:
        return float('nan')
    return mass_flow_rate / (density * flow_area)

def pressure_drop(friction_factor: float, length: float, hydraulic_diameter: float, density: float, velocity: float) -> float:
    """
    Returnerer trykkfall i kanalen.
    friction_factor: Friksjonsfaktor
    length: Lengde (m)
    hydraulic_diameter: Hydraulisk diameter (m)
    density: Tetthet (kg/m³)
    velocity: Hastighet (m/s)
    """
    if hydraulic_diameter <= 0:
        return float('nan')
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
) -> FlowResults:
    """
    Samler alle relevante strømningstall for én side og returnerer som FlowResults.
    Alle enheter SI.
    """
    re = reynolds_number(mass_flow_rate, density, dynamic_viscosity, hydraulic_diameter, flow_area)
    regime = flow_regime_from_re(re)
    pr = prandtl_number(specific_heat_capacity, dynamic_viscosity, thermal_conductivity)
    nu = nusselt_number(re, pr, regime)
    vel = velocity(mass_flow_rate, density, flow_area)
    h = nu * thermal_conductivity / hydraulic_diameter if hydraulic_diameter > 0 else float('nan')
    f = friction_factor(re, regime)
    dp = pressure_drop(f, length, hydraulic_diameter, density, vel)
    volumetric_flow_rate = mass_flow_rate / density if density > 0 else float('nan')
    mass_flux = mass_flow_rate / flow_area if flow_area > 0 else float('nan')
    return FlowResults(
        reynolds_number=re,
        flow_regime=regime,
        prandtl_number=pr,
        nusselt_number=nu,
        velocity=vel,
        heat_transfer_coefficient=h,
        friction_factor=f,
        pressure_drop=dp,
        volumetric_flow_rate=volumetric_flow_rate,
        mass_flux=mass_flux
    )
