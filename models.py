from typing import Literal
from pydantic import BaseModel

class AirStreamInput(BaseModel):
    mass_flow_rate: float
    temperature_c: float
    phi: float
    pressure: float

class ExchangerInput(BaseModel):
    width: float
    length: float
    plate_thickness: float
    thermal_conductivity_plate: float
    number_of_plates: int
    channel_height: float
    flow_arrangement: Literal["cross-flow", "counter-flow"]


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

class SimulationResult(BaseModel):
    airstream_1: AirStreamInput
    airstream_2: AirStreamInput
    exchanger: ExchangerInput
    state: HeatExchangerStateModel
