#from typing import Optional, Literal
import math

class Report:
    @staticmethod
    def print_header() -> None:
        print("="*90)
        print("PLATEVARMEVEKSLER BEREGNING - UNMIXED CROSS-FLOW")
        print("="*90)

    @staticmethod
    def print_geometry(exchanger: 'PlateHeatExchanger') -> None:
        print(f"\n{'GEOMETRISKE EGENSKAPER':^90}")
        print("-"*90)
        print(f"{'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}")
        print("-"*90)
        print(f"{'Antall kanaler':<30} {exchanger.number_of_channels_side_1:<25} {exchanger.number_of_channels_side_2:<25}")
        print(f"{'Strømningstverrsnitt [m²]':<30} {exchanger.area_flow_1:.4f}{'':<15} {exchanger.area_flow_2:.4f}{'':<15}")
        print(f"{'Kanalhøyde [mm]':<30} {exchanger.channel_height*1000:<25.1f} {exchanger.channel_height*1000:<25.1f}")
        if exchanger.hydraulic_diameter is None:
            print(f"{'Hydraulisk diameter [mm]':<30} {'IKKE BEREGNET':<25} {'IKKE BEREGNET':<25}")
        else:
            print(f"{'Hydraulisk diameter [mm]':<30} {exchanger.hydraulic_diameter*1000:<25.2f} {exchanger.hydraulic_diameter*1000:<25.2f}")
        print(f"{'Volum i veksler [m³]':<30} {exchanger.volume_total_1:.3f}{'':<15} {exchanger.volume_total_2:.3f}{'':<15}")

    @staticmethod
    def print_air_properties(airstream_1: 'AirStream', airstream_2: 'AirStream') -> None:
        print(f"\n{'LUFTPARAMETRE - GJENNOMSNITTLIG':^90}")
        print("-"*90)
        print(f"{'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}")
        print("-"*90)
        print(f"{'Temperatur [°C]':<30} {airstream_1.temperature_c:<25.1f} {airstream_2.temperature_c:<25.1f}")
        print(f"{'Tetthet [kg/m³]':<30} {airstream_1.rho:.3f}{'':<15} {airstream_2.rho:.3f}{'':<15}")
        print(f"{'Spes. varmekap. [J/kgK]':<30} {airstream_1.cp:.1f}{'':<15} {airstream_2.cp:.1f}{'':<15}")

    @staticmethod
    def print_flow_parameters(state: 'HeatExchangerState', airstream_1: 'AirStream', airstream_2: 'AirStream') -> None:
        print(f"\n{'STRØMNINGSPARAMETRE':^90}")
        print("-"*90)
        print(f"{'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}")
        print("-"*90)
        print(f"{'Massestrøm [kg/s]':<30} {airstream_1.m_dot if airstream_1 else 0:<25.3f} {airstream_2.m_dot if airstream_2 else 0:<25.3f}")
        print(f"{'Volumstrøm [m³/s]':<30} {state.q_vol_1 if state.q_vol_1 is not None else 0:.3f}{'':<15} {state.q_vol_2 if state.q_vol_2 is not None else 0:.3f}{'':<15}")
        print(f"{'Volumstrøm [m³/h]':<30} {(state.q_vol_1*3600) if state.q_vol_1 is not None else 0:.1f}{'':<15} {(state.q_vol_2*3600) if state.q_vol_2 is not None else 0:.1f}{'':<15}")
        print(f"{'Lufthastighet [m/s]':<30} {state.v_1 if state.v_1 is not None else 0:.2f}{'':<15} {state.v_2 if state.v_2 is not None else 0:.2f}{'':<15}")
        print(f"{'Massestrømhastighet [kg/m²s]':<30} {state.g_1 if state.g_1 is not None else 0:.1f}{'':<15} {state.g_2 if state.g_2 is not None else 0:.1f}{'':<15}")
        print(f"{'Reynolds tall':<30} {state.re_1 if state.re_1 is not None else 0:.0f}{'':<15} {state.re_2 if state.re_2 is not None else 0:.0f}{'':<15}")
        print(f"{'Strømningsregime':<30} {state.flow_regime_1 if state.flow_regime_1 is not None else '':<25} {state.flow_regime_2 if state.flow_regime_2 is not None else '':<25}")
        print(f"{'Nusselt tall':<30} {state.nu_1 if state.nu_1 is not None else 0:.2f}{'':<15} {state.nu_2 if state.nu_2 is not None else 0:.2f}{'':<15}")
        print(f"{'Varmeovergangstall [W/m²K]':<30} {state.h_1 if state.h_1 is not None else 0:.2f}{'':<15} {state.h_2 if state.h_2 is not None else 0:.2f}{'':<15}")
        print(f"{'Trykkfall [Pa]':<30} {state.delta_p_1 if state.delta_p_1 is not None else 0:.1f}{'':<15} {state.delta_p_2 if state.delta_p_2 is not None else 0:.1f}{'':<15}")
        print(f"{'Trykkfall [kPa]':<30} {(state.delta_p_1/1000) if state.delta_p_1 is not None else 0:.3f}{'':<15} {(state.delta_p_2/1000) if state.delta_p_2 is not None else 0:.3f}{'':<15}")
        print(f"{'Friksjonsfaktor':<30} {state.f_1 if state.f_1 is not None else 0:.4f}{'':<15} {state.f_2 if state.f_2 is not None else 0:.4f}{'':<15}")
        print(f"{'Oppholdstid [s]':<30} {state.t_res_1 if state.t_res_1 is not None else 0:.2f}{'':<15} {state.t_res_2 if state.t_res_2 is not None else 0:.2f}{'':<15}")

    @staticmethod
    def print_inlet_conditions(airstream_1: 'AirStream', airstream_2: 'AirStream') -> None:
        print(f"\n{'INNLØPSBETINGELSER':^90}")
        print("-"*90)
        print(f"{'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}")
        print("-"*90)
        print(f"{'Innløpstemperatur [°C]':<30} {airstream_1.temperature_c:<25.1f} {airstream_2.temperature_c:<25.1f}")
        print(f"{'Relativ fuktighet [%]':<30} {airstream_1.phi*100:<25.1f} {airstream_2.phi*100:<25.1f}")

    @staticmethod
    def print_thermal_resistances(state: 'HeatExchangerState') -> None:
        print(f"\n{'VARMEMOTSTANDER':^90}")
        print("-"*90)
        print(f"{'Type':<30} {'Verdi [K/W]':<25} {'Kommentar':<25}")
        print("-"*90)
        print(f"{'Konvektivt varmeovergangstall side 1':<30} {state.r_conv_1:.6f}{'':<15} {'Varm side':<25}")
        print(f"{'Konvektivt varmeovergangstall side 2':<30} {state.r_conv_2:.6f}{'':<15} {'Kald side':<25}")
        print(f"{'Konduktiv varmemotstand plate':<30} {state.r_cond:.6f}{'':<15} {'Plate':<25}")
        print(f"{'Total motstand':<30} {state.r_total:.6f}{'':<15} {'Sum':<25}")

    @staticmethod
    def print_results_summary(state: 'HeatExchangerState', exchanger: 'PlateHeatExchanger') -> None:
        print(f"\n{'RESULTATER':^90}")
        print("-"*90)
        print(f"{'Total U-verdi:':<30} {state.u_value:.2f} W/m²K")
        print(f"{'Total varmeoverflate:':<30} {exchanger.area_heat_total:.2f} m²")
        print(f"{'NTU:':<30} {state.ntu:.2f}")
        print(f"{'C_min/C_max:':<30} {state.c_min/state.c_max:.3f}")
        print(f"{'Effektivitet:':<30} {state.effectiveness*100:.1f} %")
        print(f"{'Maks varmeoverføring:':<30} {state.q_max/1000:.2f} kW")
        print(f"{'Faktisk varmeoverføring:':<30} {state.q_actual/1000:.2f} kW")

class HeatExchangerState:
    def __init__(self) -> None:
        # Strømnings- og varmeovergangsparametre for begge sider
        self.h_1: float = float("nan")
        self.re_1: float = float("nan")
        self.nu_1: float = float("nan")
        self.v_1: float = float("nan")
        self.q_vol_1: float = float("nan")
        self.g_1: float = float("nan")
        self.delta_p_1: float = float("nan")
        self.f_1: float = float("nan")
        self.flow_regime_1: str = "Unknown"

        self.h_2: float = float("nan")
        self.re_2: float = float("nan")
        self.nu_2: float = float("nan")
        self.v_2: float = float("nan")
        self.q_vol_2: float = float("nan")
        self.g_2: float = float("nan")
        self.delta_p_2: float = float("nan")
        self.f_2: float = float("nan")
        self.flow_regime_2: str = "Unknown"

        # Motstander og U-verdi
        self.r_conv_1: float = float("nan")
        self.r_conv_2: float = float("nan")
        self.r_cond: float = float("nan")
        self.r_total: float = float("nan")
        self.u_value: float = float("nan")

        # Effektivitet og varmeoverføring
        self.effectiveness: float = float("nan")
        self.ntu: float = float("nan")
        self.c_min: float = float("nan")
        self.c_max: float = float("nan")
        self.q_max: float = float("nan")
        self.q_actual: float = float("nan")

        # Oppholdstid
        self.t_res_1: float = float("nan")
        self.t_res_2: float = float("nan")

def get_flow_regime(Re: float) -> str:
    """
    Bestemmer strømningsregime basert på Reynolds tall
    """
    if Re < 2300:
        return "Laminær"
    elif 2300 <= Re <= 4000:
        return "Overgangsstrømning"
    else:
        return "Turbulent"

def calculate_flow_parameters(
    m_dot: float,
    rho: float,
    dynamic_viscocity: float,
    cp: float,
    k: float,
    Pr: float,
    hydraulic_diameter: float,
    A_flow: float
) -> tuple[float, float, float, float, float, float, float, float, float, str]:
    """
    Beregner strømningsparametre for gitt side
    """
    G = m_dot / A_flow
    V = G / rho
    Q_vol = m_dot / rho
    Re = rho * V * hydraulic_diameter / dynamic_viscocity
    flow_regime = get_flow_regime(Re)
    return Re, rho, dynamic_viscocity, cp, k, Pr, V, Q_vol, G, flow_regime

def nusselt_number(Re: float, Pr: float, flow_regime: str) -> float:
    """
    Beregner Nusselt tall basert på Reynolds og Prandtl tall
    Bruker korrelasjon for unmixed cross-flow
    """
    if flow_regime == "Laminær":
        Nu = 3.66
    elif flow_regime == "Overgangsstrømning":
        Nu_laminar = 3.66
        f = (0.79 * math.log(Re) - 1.64)**-2 if Re > 2300 else 64/Re
        Nu_turbulent = (f/8) * (Re - 1000) * Pr / (1 + 12.7 * math.sqrt(f/8) * (Pr**(2/3) - 1))
        weight = (Re - 2300) / (4000 - 2300)
        Nu = Nu_laminar + weight * (Nu_turbulent - Nu_laminar)
    else:
        f = (0.79 * math.log(Re) - 1.64)**-2
        Nu = (f/8) * (Re - 1000) * Pr / (1 + 12.7 * math.sqrt(f/8) * (Pr**(2/3) - 1))
    return Nu

def pressure_drop(
    Re: float,
    rho: float,
    V: float,
    L: float,
    D_h: float,
    flow_regime: str
) -> tuple[float, float]:
    """
    Beregner trykkfall i kanalen
    """
    if flow_regime == "Laminær":
        f = 64 / Re
    elif flow_regime == "Overgangsstrømning":
        f_laminar = 64 / Re
        f_turbulent = 0.316 * Re**(-0.25)
        weight = (Re - 2300) / (4000 - 2300)
        f = f_laminar + weight * (f_turbulent - f_laminar)
    else:
        f = 0.316 * Re**(-0.25)
    delta_p = f * (L / D_h) * (rho * V**2) / 2
    return delta_p, f

def convective_heat_transfer(
    m_dot: float,
    rho: float,
    dynamic_viscocity: float,
    cp: float,
    k: float,
    Pr: float,
    A_flow: float,
    hydraulic_diameter: float,
    length: float
) -> tuple[float, float, float, float, float, float, float, float, str]:
    """
    Beregner konvektivt varmeovergangstall for gitt side
    """
    Re, rho, dynamic_viscocity, cp, k, Pr, V, Q_vol, G, flow_regime = calculate_flow_parameters(
        m_dot, rho, dynamic_viscocity, cp, k, Pr, hydraulic_diameter, A_flow
    )
    Nu = nusselt_number(Re, Pr, flow_regime)
    h = Nu * k / hydraulic_diameter
    delta_p, f = pressure_drop(Re, rho, V, length, hydraulic_diameter, flow_regime)
    return h, Re, Nu, V, Q_vol, G, delta_p, f, flow_regime

class AirProperties:
    def __init__(self, temperature_c: float, phi: float, pressure: float) -> None:
        self.temperature_c = temperature_c
        self.phi = phi
        self.pressure = pressure
        self.rho = float("nan")
        self.dynamic_viscosity = float("nan")
        self.cp = float("nan")
        self.k = float("nan")
        self.prandtl = float("nan")
        self._calculate()

    def _calculate(self) -> None:
        """
        Beregn og sett luftens egenskaper som attributter.
        """
        T_k = self.temperature_c + 273.15  # Kelvin
        # Ideell gasslov for tetthet
        self.rho = self.pressure / (287.05 * T_k)
        # Sutherland's formel for viskositet
        mu_ref = 1.716e-5
        T0 = 273.15
        S = 110.4
        self.dynamic_viscosity = mu_ref * ((T0 + S) / (T_k + S)) * ((T_k / T0) ** 1.5)
        # Spesifikk varmekapasitet
        self.cp = 1005 + 0.05 * (self.temperature_c - 20)
        # Termisk konduktivitet
        self.k = 0.024 + 0.00007 * self.temperature_c
        # Prandtl-tall
        self.prandtl = 0.7 + 0.0002 * self.temperature_c

class AirStream:
    def __init__ (self, m_dot: float, air_properties: AirProperties) -> None:
        self.m_dot = m_dot
        self.air = air_properties
    @property
    def mass_flow_rate(self) -> float:
        return self.m_dot
    @property
    def temperature_c(self) -> float:
        return self.air.temperature_c
    @property
    def phi(self) -> float:
        return self.air.phi
    @property
    def pressure(self) -> float:
        return self.air.pressure
    @property
    def rho(self) -> float:
        return self.air.rho
    @property
    def dynamic_viscosity(self) -> float:
        return self.air.dynamic_viscosity
    @property
    def cp(self) -> float:
        return self.air.cp
    @property
    def k(self) -> float:
        return self.air.k
    @property
    def prandtl(self) -> float:
        return self.air.prandtl

class PlateHeatExchanger:
    def __init__(self) -> None:
        # Geometriske parametre
        self.width = 1.4          # Bredde [m]
        self.length = 1.4         # Lengde [m]
        self.plate_thickness = 0.0005  # Platetykkelse [m]
        self.thermal_conductivity_plate = 15.0   # Varmeledningsevne plate [W/mK]
        self.number_of_plates = 30           # Antall plater (starter med stor N)
        self.channel_height = 0.005  # Kanalhøyde [m] (typisk verdi)

    @property
    def number_of_channels_side_1(self) -> int:
        return math.ceil((self.number_of_plates + 1) / 2)
    @property
    def number_of_channels_side_2(self) -> int:
        return math.floor((self.number_of_plates + 1) / 2)
    @property
    def area_heat_total(self) -> float:
        return self.number_of_plates * 2 * self.width * self.length
    @property
    def area_heat_1(self) -> float:
        return self.number_of_plates * self.width * self.length
    @property
    def area_heat_2(self) -> float:
        return self.number_of_plates * self.width * self.length
    @property
    def volume_channel(self) -> float:
        return self.area_flow_channel * self.length
    @property
    def volume_total_1(self) -> float:
        return self.number_of_channels_side_1 * self.volume_channel
    @property
    def volume_total_2(self) -> float:
        return self.number_of_channels_side_2 * self.volume_channel 
    @property
    def volume_total(self) -> float:
        return self.volume_total_1 + self.volume_total_2
    @property
    def volume_ratio(self) -> float:
        return self.volume_total_1 / self.volume_total_2 if self.volume_total_2 != 0 else float("inf")
    @property
    def area_ratio(self) -> float:
        return self.area_heat_1 / self.area_heat_2 if self.area_heat_2 != 0 else float("inf")
    @property
    def channel_ratio(self) -> float:   
        return self.number_of_channels_side_1 / self.number_of_channels_side_2 if self.number_of_channels_side_2 != 0 else float("inf")
    @property
    def area_flow_channel(self) -> float:
        return self.width * self.channel_height

    @property
    def area_flow_1(self) -> float:
        return self.number_of_channels_side_1 * self.area_flow_channel
    @property
    def area_flow_2(self) -> float:
        return self.number_of_channels_side_2 * self.area_flow_channel
    @property
    def hydraulic_diameter(self) -> float:
        return 2 * (self.width * self.channel_height) / (self.width + self.channel_height)
    @property
    def area_plate(self) -> float:
        return 2 * self.width * self.length

    def calculate_state(
        self,
        airstream_1_average: 'AirStream',
        airstream_2_average: 'AirStream'
    ) -> 'HeatExchangerState':
        """
        Beregner og returnerer et HeatExchangerState-objekt for gitte luftstrømmer.
        """
        state = HeatExchangerState()
        # Strømnings- og varmeovergangsparametre
        (
            state.h_1, state.re_1, state.nu_1, state.v_1, state.q_vol_1, state.g_1, state.delta_p_1, state.f_1, state.flow_regime_1
        ) = convective_heat_transfer(
            airstream_1_average.m_dot,
            airstream_1_average.rho,
            airstream_1_average.dynamic_viscosity,
            airstream_1_average.cp,
            airstream_1_average.k,
            airstream_1_average.prandtl,
            self.area_flow_1,
            self.hydraulic_diameter,
            self.length
        )
        (
            state.h_2, state.re_2, state.nu_2, state.v_2, state.q_vol_2, state.g_2, state.delta_p_2, state.f_2, state.flow_regime_2
        ) = convective_heat_transfer(
            airstream_2_average.m_dot,
            airstream_2_average.rho,
            airstream_2_average.dynamic_viscosity,
            airstream_2_average.cp,
            airstream_2_average.k,
            airstream_2_average.prandtl,
            self.area_flow_2,
            self.hydraulic_diameter,
            self.length
        )
        # Motstander og U-verdi
        state.r_conv_1 = 1 / (state.h_1 * self.area_heat_1)
        state.r_conv_2 = 1 / (state.h_2 * self.area_heat_2)
        state.r_cond = self.plate_thickness / (self.thermal_conductivity_plate * self.area_heat_1)
        state.r_total = state.r_conv_1 + state.r_cond + state.r_conv_2
        state.u_value = 1 / (state.r_total * self.area_heat_1)
        # Effektivitet og varmeoverføring
        c_1 = airstream_1_average.m_dot * airstream_1_average.cp
        c_2 = airstream_2_average.m_dot * airstream_2_average.cp
        state.c_min = min(c_1, c_2)
        state.c_max = max(c_1, c_2)
        c_r = state.c_min / state.c_max
        state.ntu = state.u_value * self.area_heat_1 / state.c_min
        state.effectiveness = 1 - math.exp((1/c_r) * state.ntu**0.22 * (math.exp(-c_r * state.ntu**0.78) - 1))
        state.q_max = state.c_min * (airstream_1_average.temperature_c - airstream_2_average.temperature_c)
        state.q_actual = state.effectiveness * state.q_max
        # Oppholdstid
        state.t_res_1 = self.length / state.v_1
        state.t_res_2 = self.length / state.v_2
        return state

    
    def print_results(
        self,
        state: 'HeatExchangerState',
        airstream_1_average: 'AirStream',
        airstream_2_average: 'AirStream'
    ) -> None:
        """
        Skriver ut resultater i tabellform med to kolonner.
        Deler opp utskriften i mindre metoder for bedre oversikt og utvidbarhet.
        """
        Report.print_header()
        Report.print_geometry(self)
        Report.print_air_properties(airstream_1_average, airstream_2_average)
        Report.print_flow_parameters(state, airstream_1_average, airstream_2_average)
        Report.print_inlet_conditions(airstream_1_average, airstream_2_average)
        Report.print_thermal_resistances(state)
        Report.print_results_summary(state, self)
        print("\n" + "="*90)

# Kjør en eksampelberegning
if __name__ == "__main__":
    airstream_1 = AirStream(
        m_dot=0.5,
        air_properties=AirProperties(
            temperature_c=80.0,
            phi=0.3,
            pressure=101325
        )
    )
    airstream_2 = AirStream(
        m_dot=0.6,
        air_properties=AirProperties(
            temperature_c=20.0,
            phi=0.5,
            pressure=101325
        )
    )
    phex = PlateHeatExchanger()
    
    state = phex.calculate_state(airstream_1, airstream_2)
    
    phex.print_results(state, airstream_1, airstream_2)