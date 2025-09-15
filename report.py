from typing import TYPE_CHECKING
from heatecxhanger import FlowArrangement
if TYPE_CHECKING:
    from heatecxhanger import PlateHeatExchanger
    from moistair import AirStream
    # HeatExchangerState er dynamisk, men kan evt. importeres hvis den finnes


class Report:
    @staticmethod
    def print_input_summary(airstream_1: 'AirStream', airstream_2: 'AirStream', exchanger: 'PlateHeatExchanger') -> None:
        print(f"{'INNDATA':^90}")
        print("-"*90)
        print(f"{'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}")
        print("-"*90)
        print(f"{'Massestrøm [kg/s]':<30} {airstream_1.m_dot:<25.3f} {airstream_2.m_dot:<25.3f}")
        print(f"{'Temperatur [°C]':<30} {airstream_1.temperature_c:<25.1f} {airstream_2.temperature_c:<25.1f}")
        print(f"{'Relativ fuktighet [%]':<30} {airstream_1.phi*100:<25.1f} {airstream_2.phi*100:<25.1f}")
        print(f"{'Trykk [Pa]':<30} {airstream_1.pressure:<25.0f} {airstream_2.pressure:<25.0f}")
        print("-"*90)
        for k, v in exchanger.__dict__.items():
            if isinstance(v, float):
                print(f"{k:<30} {v:<25.4f}")
            else:
                print(f"{k:<30} {str(v):<25}")
    @staticmethod
    def print_header(flow_arrangement: "FlowArrangement") -> None:
        print("="*90)
        print(f"PLATEVARMEVEKSLER BEREGNING - {flow_arrangement.name.replace('_', ' ').upper()}")
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
        print(f"\n{'LUFTPARAMETRE - INNLØP':^90}")
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
        
    @staticmethod
    def print_all(
        exchanger,
        state: 'HeatExchangerState',
        airstream_1: 'AirStream',
        airstream_2: 'AirStream',
        flow_arrangement: "FlowArrangement"
    ) -> None:
        """
        Skriver ut resultater i tabellform med to kolonner.
        Deler opp utskriften i mindre metoder for bedre oversikt og utvidbarhet.
        """
        Report.print_input_summary(airstream_1, airstream_2, exchanger)
        Report.print_header(flow_arrangement)
        Report.print_geometry(exchanger)
        Report.print_air_properties(airstream_1, airstream_2)
        Report.print_flow_parameters(state, airstream_1, airstream_2)
        Report.print_inlet_conditions(airstream_1, airstream_2)
        Report.print_thermal_resistances(state)
        Report.print_results_summary(state, exchanger)
        print("\n" + "="*90)

