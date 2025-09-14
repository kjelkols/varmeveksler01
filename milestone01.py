import numpy as np
import math
from scipy.optimize import bisect

class PlateHeatExchanger:
    def __init__(self):
            # Geometriske parametre
        self.width = 1.4          # Bredde [m]
        self.length = 1.4         # Lengde [m]
        self.plate_thickness = 0.0005  # Platetykkelse [m]
        self.thermal_conductivity_plate = 15.0   # Varmeledningsevne plate [W/mK]
        self.number_of_plates = 30           # Antall plater (starter med stor N)
        self.channel_height = 0.005  # Kanalhøyde [m] (typisk verdi)
            
        # Strømningsparametre - side 1 (varm)
        self.m_dot_1 = 0.5     # Massestrøm side 1 [kg/s]
        self.temperature_in_1 = 80.0     # Innløpstemperatur side 1 [°C]
        self.phi_in_1 = 0.3    # Relativ fuktighet side 1 [%]
        self.pressure_1 = 101325  # Innløpstrykk side 1 [Pa]
        
        # Strømningsparametre - side 2 (kald)
        self.m_dot_2 = 0.6     # Massestrøm side 2 [kg/s]
        self.temperature_in_2 = 20.0     # Innløpstemperatur side 2 [°C]
        self.phi_in_2 = 0.5    # Relativ fuktighet side 2 [%]
        self.pressure_2 = 101325  # Innløpstrykk side 2 [Pa]
            
        # Beregnede parametre for geometri
        self.area_flow_1 = None    # Strømningstverrsnitt side 1 [m²]
        self.area_flow_2 = None    # Strømningstverrsnitt side 2 [m²]
        self.area_heat_transfer = None    # Varmeoverflateareal [m²]
        self.hydraulic_diameter = None       # Hydraulisk diameter [m]

        # Beregnede parametre for strømningsside 1
        self.rho_1_avg = None    # Tetthet luft side 1 [kg/m³]
        self.cp_1_avg = None    # Spesifikk varmekapasitet luft side 1 [J/kgK]

        # Beregnede parametre for strømningsside 2
        self.rho_2_avg = None    # Tetthet luft side 2 [kg/m³]
        self.cp_2_avg = None    # Spesifikk varmekapasitet luft side 2 [J/kgK]  
        
            # Initialiser beregnede verdier
        self.calculate_geometry()
    
    def calculate_geometry(self):
        """Beregner geometriske egenskaper for varmeveksleren"""
        # Strømningstverrsnitt per kanal
        self.area_flow_channel = self.width * self.channel_height
        
        # Total strømningstverrsnitt (for N plater: N+1 kanaler, delt mellom to sider)
        self.number_of_channels_side_1 = math.ceil((self.number_of_plates + 1) / 2)
        self.number_of_channels_side_2 = math.floor((self.number_of_plates + 1) / 2)
        self.area_flow_1 = self.number_of_channels_side_1 * self.area_flow_channel
        self.area_flow_2 = self.number_of_channels_side_2 * self.area_flow_channel
        
        # Hydraulisk diameter (for rektangulær kanal)
        self.hydraulic_diameter = 2 * (self.width * self.channel_height) / (self.width + self.channel_height)
    # Varmeoverflateareal per plate (to sider)
        area_plate = 2 * self.width * self.length
    # Total varmeoverflateareal
        self.area_heat_total = self.number_of_plates * area_plate
    # Varmeoverflateareal per side
        self.area_heat_1 = self.number_of_plates * self.width * self.length
        self.area_heat_2 = self.number_of_plates * self.width * self.length
        
        # Volum per kanal
        self.volume_channel = self.area_flow_channel * self.length
    # Total volum side 1 og 2
        self.volume_total_1 = self.number_of_channels_side_1 * self.volume_channel
        self.volume_total_2 = self.number_of_channels_side_2 * self.volume_channel
    
    def air_properties(self, T, pressure):
        """
        Beregner luftegenskaper ved gitt temperatur
        T: Temperatur [°C]
        Returnerer: rho, dynamic_viscocity, c_p, k, Pr
        """
        T_k = T + 273.15  # Konverter til Kelvin
        
        # Forenklet modell for luftegenskaper
        air_density = pressure / (287.05 * T_k)  # Ideell gasslov
        
        # Dynamisk viskositet (Sutherland's formel for luft)
        dynamic_viscosity_ref = 1.716e-5  # Referanseviskositet ved 273K [Pa·s]
        T0 = 273.15    # Referansetemperatur [K]
        S = 110.4      # Sutherland temperatur [K]
        dynamic_viscocity = dynamic_viscosity_ref * ((T0 + S) / (T_k + S)) * ((T_k / T0)**1.5)
        
        # Spesifikk varmekapasitet
        c_p = 1005 + 0.05*(T - 20)  # [J/kgK]
        
        # Termisk konduktivitet
        k = 0.024 + 0.00007*T  # [W/mK]
        
        # Prandtl tall
        Pr = 0.7 + 0.0002*T
        
        return air_density, dynamic_viscocity, c_p, k, Pr
    
    def get_flow_regime(self, Re):
        """
        Bestemmer strømningsregime basert på Reynolds tall
        """
        if Re < 2300:
            return "Laminær"
        elif 2300 <= Re <= 4000:
            return "Overgangsstrømning"
        else:
            return "Turbulent"
    
    def calculate_flow_parameters(self, m_dot, T, pressure, side):
        """
        Beregner strømningsparametre for gitt side
        """
        rho, dynamic_viscocity, c_p, k, Pr = self.air_properties(T, pressure)
        
        if side == 1:
            A_flow = self.area_flow_1
        else:
            A_flow = self.area_flow_2
        
        # Massestrømhastighet
        G = m_dot / A_flow
        
        # Lufthastighet
        V = G / rho
        
        # Volumstrøm
        Q_vol = m_dot / rho
        
        # Reynolds tall
        Re = rho * V * self.hydraulic_diameter / dynamic_viscocity
        
        # Strømningsregime
        flow_regime = self.get_flow_regime(Re)
        
        return Re, rho, dynamic_viscocity, c_p, k, Pr, V, Q_vol, G, flow_regime
    
    def nusselt_number(self, Re, Pr, flow_regime):
        """
        Beregner Nusselt tall basert på Reynolds og Prandtl tall
        Bruker korrelasjon for unmixed cross-flow
        """
        if flow_regime == "Laminær":
            # Laminær strømning korrelasjon
            Nu = 3.66  # For konstant veggfluks i rektangulært rør
        elif flow_regime == "Overgangsstrømning":
            # Interpolasjon mellom laminær og turbulent
            Nu_laminar = 3.66
            # Turbulent strømning korrelasjon (Gnielinski)
            f = (0.79 * math.log(Re) - 1.64)**-2 if Re > 2300 else 64/Re
            Nu_turbulent = (f/8) * (Re - 1000) * Pr / (1 + 12.7 * math.sqrt(f/8) * (Pr**(2/3) - 1))
            
            # Lineær interpolasjon mellom 2300 og 4000
            weight = (Re - 2300) / (4000 - 2300)
            Nu = Nu_laminar + weight * (Nu_turbulent - Nu_laminar)
        else:
            # Turbulent strømning korrelasjon (Gnielinski for rør, tilpasset)
            f = (0.79 * math.log(Re) - 1.64)**-2
            Nu = (f/8) * (Re - 1000) * Pr / (1 + 12.7 * math.sqrt(f/8) * (Pr**(2/3) - 1))
        
        return Nu
    
    def pressure_drop(self, Re, rho, V, L, D_h, flow_regime):
        """
        Beregner trykkfall i kanalen
        """
        if flow_regime == "Laminær":
            # Laminær strømning
            f = 64 / Re
        elif flow_regime == "Overgangsstrømning":
            # Interpolasjon mellom laminær og turbulent
            f_laminar = 64 / Re
            f_turbulent = 0.316 * Re**(-0.25)
            weight = (Re - 2300) / (4000 - 2300)
            f = f_laminar + weight * (f_turbulent - f_laminar)
        else:
            # Turbulent strømning (Blasius korrelasjon)
            f = 0.316 * Re**(-0.25)
        
        # Trykkfall
        delta_p = f * (L / D_h) * (rho * V**2) / 2
        
        return delta_p, f
    
    def convective_heat_transfer(self, m_dot, T, pressure, side):
        """
        Beregner konvektivt varmeovergangstall for gitt side
        """
        # Beregn strømningsparametre
        Re, rho, dynamic_viscocity, c_p, k, Pr, V, Q_vol, G, flow_regime = self.calculate_flow_parameters(m_dot, T, pressure, side)
        
        # Beregn Nusselt tall
        Nu = self.nusselt_number(Re, Pr, flow_regime)
        
        # Beregn konvektivt varmeovergangstall
        h = Nu * k / self.hydraulic_diameter
        
        # Beregn trykkfall
        delta_p, f = self.pressure_drop(Re, rho, V, self.length, self.hydraulic_diameter, flow_regime)

        return h, Re, Nu, V, Q_vol, G, delta_p, f, flow_regime
    
    def calculate_resistances(self):
        """
        Beregner alle varmemotstander og U-verdi for varmeveksleren.
        Deler opp i mindre metoder for bedre lesbarhet og utvidbarhet.
        """
        self.set_average_temperatures()
        self.set_average_air_properties()
        self.set_convective_parameters()
        self.set_thermal_resistances()
        self.set_overall_U_value()

    def set_average_temperatures(self):
        """Setter gjennomsnittstemperaturer for begge sider."""
        self.T_avg1 = (self.temperature_in_1 + self.temperature_in_2) / 2
        self.T_avg2 = (self.temperature_in_1 + self.temperature_in_2) / 2

    def set_average_air_properties(self):
        """Beregner og lagrer gjennomsnittlige luftegenskaper for begge sider."""
        self.rho_1_avg, self.air_viscosity_avg_1, self.cp_1_avg, self.k1_avg, self.Pr1_avg = self.air_properties(self.T_avg1, self.pressure_1)
        self.rho_2_avg, self.air_viscosity_avg_2, self.cp_2_avg, self.k2_avg, self.Pr2_avg = self.air_properties(self.T_avg2, self.pressure_2)

    def set_convective_parameters(self):
        """Beregner og lagrer konvektive varmeovergangstall og strømningsparametre for begge sider."""
        (
            self.h_1, self.re_1, self.nu_1, self.v_1, self.q_vol_1, self.g_1, self.delta_p_1, self.f_1, self.flow_regime_1
        ) = self.convective_heat_transfer(self.m_dot_1, self.T_avg1, self.pressure_1, 1)
        (
            self.h_2, self.re_2, self.nu_2, self.v_2, self.q_vol_2, self.g_2, self.delta_p_2, self.f_2, self.flow_regime_2
        ) = self.convective_heat_transfer(self.m_dot_2, self.T_avg2, self.pressure_2, 2)

    def set_thermal_resistances(self):
        """Beregner og lagrer varmemotstander for begge sider og platen."""
        self.r_conv_1 = 1 / (self.h_1 * self.area_heat_1)
        self.r_conv_2 = 1 / (self.h_2 * self.area_heat_2)
        self.r_cond = self.plate_thickness / (self.thermal_conductivity_plate * self.area_heat_1)
        self.r_total = self.r_conv_1 + self.r_cond + self.r_conv_2

    def set_overall_U_value(self):
        """Beregner og lagrer total U-verdi for varmeveksleren."""
        self.u_value = 1 / (self.r_total * self.area_heat_1)
    
    def calculate_effectiveness(self):
        """
        Beregner effektivitet for varmeveksleren (NTU-metode)
        """
        # Bruk gjennomsnittlige varmekapasiteter
        c_1 = self.m_dot_1 * self.cp_1_avg
        c_2 = self.m_dot_2 * self.cp_2_avg
        c_min = min(c_1, c_2)
        c_max = max(c_1, c_2)
        c_r = c_min / c_max
        # Beregn NTU
        ntu = self.u_value * self.area_heat_1 / c_min
        # Beregn effektivitet for unmixed-unmixed cross-flow
        effectiveness = 1 - math.exp((1/c_r) * ntu**0.22 * (math.exp(-c_r * ntu**0.78) - 1))
        # Beregn teoretisk maksimal varmeoverføring
        q_max = c_min * (self.temperature_in_1 - self.temperature_in_2)
        q_actual = effectiveness * q_max
        return effectiveness, ntu, c_min, c_max, q_max, q_actual
    
    def calculate_residence_time(self):
        """
        Beregner oppholdstid for luft i varmeveksleren
        """
        # Gjennomsnittlig hastighet
        v_avg_1 = self.v_1
        v_avg_2 = self.v_2
        # Oppholdstid
        t_res_1 = self.length / v_avg_1
        t_res_2 = self.length / v_avg_2
        return t_res_1, t_res_2
    
    def print_results(self):
        """
        Skriver ut resultater i tabellform med to kolonner.
        Deler opp utskriften i mindre metoder for bedre oversikt og utvidbarhet.
        """
        effectiveness, ntu, c_min, c_max, q_max, q_actual = self.calculate_effectiveness()
        t_res_1, t_res_2 = self.calculate_residence_time()
        self.print_header()
        self.print_geometry()
        self.print_air_properties()
        self.print_flow_parameters(t_res_1, t_res_2)
        self.print_inlet_conditions()
        self.print_thermal_resistances()
        self.print_results_summary(effectiveness, ntu, c_min, c_max, q_max, q_actual)
        print("\n" + "="*90)

    def print_header(self):
        print("="*90)
        print("PLATEVARMEVEKSLER BEREGNING - UNMIXED CROSS-FLOW")
        print("="*90)

    def print_geometry(self):
        print(f"\n{'GEOMETRISKE EGENSKAPER':^90}")
        print("-"*90)
        print(f"{'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}")
        print("-"*90)
        print(f"{'Antall kanaler':<30} {self.number_of_channels_side_1:<25} {self.number_of_channels_side_2:<25}")
        print(f"{'Strømningstverrsnitt [m²]':<30} {self.area_flow_1:.4f}{'':<15} {self.area_flow_2:.4f}{'':<15}")
        print(f"{'Kanalhøyde [mm]':<30} {self.channel_height*1000:<25.1f} {self.channel_height*1000:<25.1f}")
        if self.hydraulic_diameter is None:
            print(f"{'Hydraulisk diameter [mm]':<30} {'IKKE BEREGNET':<25} {'IKKE BEREGNET':<25}")
        else:
            print(f"{'Hydraulisk diameter [mm]':<30} {self.hydraulic_diameter*1000:<25.2f} {self.hydraulic_diameter*1000:<25.2f}")
        print(f"{'Volum i veksler [m³]':<30} {self.volume_total_1:.3f}{'':<15} {self.volume_total_2:.3f}{'':<15}")

    def print_air_properties(self):
        print(f"\n{'LUFTPARAMETRE - GJENNOMSNITTLIG':^90}")
        print("-"*90)
        print(f"{'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}")
        print("-"*90)
        print(f"{'Temperatur [°C]':<30} {self.T_avg1:<25.1f} {self.T_avg2:<25.1f}")
        print(f"{'Tetthet [kg/m³]':<30} {self.rho_1_avg:.3f}{'':<15} {self.rho_2_avg:.3f}{'':<15}")
        print(f"{'Spes. varmekap. [J/kgK]':<30} {self.cp_1_avg:.1f}{'':<15} {self.cp_2_avg:.1f}{'':<15}")

    def print_flow_parameters(self, t_res_1, t_res_2):
        print(f"\n{'STRØMNINGSPARAMETRE':^90}")
        print("-"*90)
        print(f"{'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}")
        print("-"*90)
        print(f"{'Massestrøm [kg/s]':<30} {self.m_dot_1:<25.3f} {self.m_dot_2:<25.3f}")
        print(f"{'Volumstrøm [m³/s]':<30} {self.q_vol_1:.3f}{'':<15} {self.q_vol_2:.3f}{'':<15}")
        print(f"{'Volumstrøm [m³/h]':<30} {self.q_vol_1*3600:.1f}{'':<15} {self.q_vol_2*3600:.1f}{'':<15}")
        print(f"{'Lufthastighet [m/s]':<30} {self.v_1:.2f}{'':<15} {self.v_2:.2f}{'':<15}")
        print(f"{'Massestrømhastighet [kg/m²s]':<30} {self.g_1:.1f}{'':<15} {self.g_2:.1f}{'':<15}")
        print(f"{'Reynolds tall':<30} {self.re_1:.0f}{'':<15} {self.re_2:.0f}{'':<15}")
        print(f"{'Strømningsregime':<30} {self.flow_regime_1:<25} {self.flow_regime_2:<25}")
        print(f"{'Nusselt tall':<30} {self.nu_1:.2f}{'':<15} {self.nu_2:.2f}{'':<15}")
        print(f"{'Varmeovergangstall [W/m²K]':<30} {self.h_1:.2f}{'':<15} {self.h_2:.2f}{'':<15}")
        print(f"{'Trykkfall [Pa]':<30} {self.delta_p_1:.1f}{'':<15} {self.delta_p_2:.1f}{'':<15}")
        print(f"{'Trykkfall [kPa]':<30} {self.delta_p_1/1000:.3f}{'':<15} {self.delta_p_2/1000:.3f}{'':<15}")
        print(f"{'Friksjonsfaktor':<30} {self.f_1:.4f}{'':<15} {self.f_2:.4f}{'':<15}")
        print(f"{'Oppholdstid [s]':<30} {t_res_1:.2f}{'':<15} {t_res_2:.2f}{'':<15}")

    def print_inlet_conditions(self):
        print(f"\n{'INNLØPSBETINGELSER':^90}")
        print("-"*90)
        print(f"{'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}")
        print("-"*90)
        print(f"{'Innløpstemperatur [°C]':<30} {self.temperature_in_1:<25.1f} {self.temperature_in_2:<25.1f}")
        print(f"{'Relativ fuktighet [%]':<30} {self.phi_in_1*100:<25.1f} {self.phi_in_2*100:<25.1f}")

    def print_thermal_resistances(self):
        print(f"\n{'VARMEMOTSTANDER':^90}")
        print("-"*90)
        print(f"{'Type':<30} {'Verdi [K/W]':<25} {'Kommentar':<25}")
        print("-"*90)
        print(f"{'Konvektivt varmeovergangstall side 1':<30} {self.r_conv_1:.6f}{'':<15} {'Varm side':<25}")
        print(f"{'Konvektivt varmeovergangstall side 2':<30} {self.r_conv_2:.6f}{'':<15} {'Kald side':<25}")
        print(f"{'Konduktiv varmemotstand plate':<30} {self.r_cond:.6f}{'':<15} {'Plate':<25}")
        print(f"{'Total motstand':<30} {self.r_total:.6f}{'':<15} {'Sum':<25}")

    def print_results_summary(self, effectiveness, ntu, c_min, c_max, q_max, q_actual):
        print(f"\n{'RESULTATER':^90}")
        print("-"*90)
        print(f"{'Total U-verdi:':<30} {self.u_value:.2f} W/m²K")
        print(f"{'Total varmeoverflate:':<30} {self.area_heat_total:.2f} m²")
        print(f"{'NTU:':<30} {ntu:.2f}")
        print(f"{'C_min/C_max:':<30} {c_min/c_max:.3f}")
        print(f"{'Effektivitet:':<30} {effectiveness*100:.1f} %")
        print(f"{'Maks varmeoverføring:':<30} {q_max/1000:.2f} kW")
        print(f"{'Faktisk varmeoverføring:':<30} {q_actual/1000:.2f} kW")
        
    # ...existing code...
        
# Kjør beregningen
if __name__ == "__main__":
    phex = PlateHeatExchanger()
    phex.calculate_resistances()
    phex.print_results()