from typing import Literal
from pydantic import BaseModel

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
