from pydantic import BaseModel
from definitions import FlowArrangement

class AirStreamInput(BaseModel):
    mass_flow_rate: float
    temperature_c: float
    phi: float
    pressure: float

class AirStreamOutput(BaseModel):
    """Pydantic-modell for en luftstrøm med alle beregnede egenskaper."""
    mass_flow_rate: float
    temperature_c: float
    phi: float
    pressure: float
    rho: float
    dynamic_viscosity: float
    cp: float
    k: float
    prandtl: float

class ExchangerInput(BaseModel):
    width: float
    length: float
    plate_thickness: float
    thermal_conductivity_plate: float
    number_of_plates: int
    channel_height: float

class HeatExchangerSide(BaseModel):
    """

    Samler alle relevante strømning- og varmeovergangsparametre for én side av varmeveksleren.

    Attributter:
        h: Varmeovergangstall [W/m2K]
        re: Reynolds-tall [-]
        nu: Nusselt-tall [-]
        v: Gjennomsnittlig hastighet [m/s]
        q_vol: Volumstrøm [m3/s]
        g: Massefluks [kg/m2s]
        delta_p: Trykkfall [Pa]
        f: Friksjonsfaktor [-]
        flow_regime: Strømningsregime (f.eks. "laminar", "turbulent")
    """
    h: float
    re: float
    nu: float
    v: float
    q_vol: float
    g: float
    delta_p: float
    f: float
    flow_regime: str

class HeatExchangerStateModel(BaseModel):
    side_1: HeatExchangerSide
    side_2: HeatExchangerSide
    r_conv_1: float
    r_conv_2: float
    r_cond: float
    r_total: float
    u_value: float
    effectiveness: float
    ntu: float
    c_min: float
    c_max: float
    q_max: float
    q_actual: float
    t_res_1: float
    t_res_2: float

class SimulationInput(BaseModel):
    airstream_1: AirStreamInput
    airstream_2: AirStreamInput
    exchanger: ExchangerInput
    flow_arrangement: FlowArrangement

class SimulationResult(BaseModel):
    airstream_1: AirStreamInput
    airstream_2: AirStreamInput
    exchanger: ExchangerInput
    state: HeatExchangerStateModel
    
class HeatExchangerParameters(BaseModel):
    h_1: float
    re_1: float
    nu_1: float
    v_1: float
    q_vol_1: float
    g_1: float
    delta_p_1: float
    f_1: float
    flow_regime_1: str
    h_2: float
    re_2: float
    nu_2: float
    v_2: float
    q_vol_2: float
    g_2: float
    delta_p_2: float
    f_2: float
    flow_regime_2: str
    r_conv_1: float
    r_conv_2: float
    r_cond: float
    r_total: float
    u_value: float
    ntu: float
    c_min: float
    c_max: float
    area_heat_1: float
    area_heat_2: float
    t_res_1: float
    t_res_2: float

class HeatExchangerResults(BaseModel):
    effectiveness: float
    q_max: float
    q_actual: float
    # Her kan du legge til flere resultater, f.eks. utgående temperaturer