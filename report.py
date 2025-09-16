from typing import TYPE_CHECKING
from definitions import FlowArrangement
if TYPE_CHECKING:
    from heatecxhanger import PlateHeatExchanger
    from moistair import AirStream
    # HeatExchangerState er dynamisk, men kan evt. importeres hvis den finnes


class Report:
    @staticmethod
    def get_input_summary_string(airstream_1: 'AirStream', airstream_2: 'AirStream', exchanger: 'PlateHeatExchanger') -> str:
        lines = []
        lines.append(f"{ 'INNDATA':^90}")
        lines.append("-"*90)
        lines.append(f"{ 'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}")
        lines.append("-"*90)
        lines.append(f"{ 'Massestrøm [kg/s]':<30} {airstream_1.m_dot:<25.3f} {airstream_2.m_dot:<25.3f}")
        lines.append(f"{ 'Temperatur [°C]':<30} {airstream_1.temperature_c:<25.1f} {airstream_2.temperature_c:<25.1f}")
        lines.append(f"{ 'Relativ fuktighet [%]':<30} {airstream_1.phi*100:<25.1f} {airstream_2.phi*100:<25.1f}")
        lines.append(f"{ 'Trykk [Pa]':<30} {airstream_1.pressure:<25.0f} {airstream_2.pressure:<25.0f}")
        lines.append("-"*90)
        for k, v in exchanger.__dict__.items():
            if isinstance(v, float):
                lines.append(f"{k:<30} {v:<25.4f}")
            else:
                lines.append(f"{k:<30} {str(v):<25}")
        return "\n".join(lines)

    @staticmethod
    def print_input_summary(airstream_1: 'AirStream', airstream_2: 'AirStream', exchanger: 'PlateHeatExchanger') -> None:
        print(Report.get_input_summary_string(airstream_1, airstream_2, exchanger))

    @staticmethod
    def get_header_string(flow_arrangement: "FlowArrangement") -> str:
        return "\n".join([
            "="*90,
            f"PLATEVARMEVEKSLER BEREGNING - {flow_arrangement.name.replace('_', ' ').upper()}",
            "="*90
        ])

    @staticmethod
    def print_header(flow_arrangement: "FlowArrangement") -> None:
        print(Report.get_header_string(flow_arrangement))

    @staticmethod
    def get_geometry_string(exchanger: 'PlateHeatExchanger') -> str:
        lines = [
            f"\n{'GEOMETRISKE EGENSKAPER':^90}",
            "-"*90,
            f"{ 'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}",
            "-"*90,
            f"{ 'Antall kanaler':<30} {exchanger.number_of_channels_side_1:<25} {exchanger.number_of_channels_side_2:<25}",
            f"{ 'Strømningstverrsnitt [m²]':<30} {exchanger.area_flow_1:.4f}{'':<15} {exchanger.area_flow_2:.4f}{'':<15}",
            f"{ 'Kanalhøyde [mm]':<30} {exchanger.channel_height*1000:<25.1f} {exchanger.channel_height*1000:<25.1f}"
        ]
        if exchanger.hydraulic_diameter is None:
            lines.append(f"{ 'Hydraulisk diameter [mm]':<30} {'IKKE BEREGNET':<25} {'IKKE BEREGNET':<25}")
        else:
            lines.append(f"{ 'Hydraulisk diameter [mm]':<30} {exchanger.hydraulic_diameter*1000:<25.2f} {exchanger.hydraulic_diameter*1000:<25.2f}")
        lines.append(f"{ 'Volum i veksler [m³]':<30} {exchanger.volume_total_1:.3f}{'':<15} {exchanger.volume_total_2:.3f}{'':<15}")
        return "\n".join(lines)

    @staticmethod
    def print_geometry(exchanger: 'PlateHeatExchanger') -> None:
        print(Report.get_geometry_string(exchanger))

    @staticmethod
    def get_air_properties_string(airstream_1: 'AirStream', airstream_2: 'AirStream') -> str:
        return "\n".join([
            f"\n{'LUFTPARAMETRE - INNLØP':^90}",
            "-"*90,
            f"{ 'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}",
            "-"*90,
            f"{ 'Temperatur [°C]':<30} {airstream_1.temperature_c:<25.1f} {airstream_2.temperature_c:<25.1f}",
            f"{ 'Tetthet [kg/m³]':<30} {airstream_1.rho:.3f}{'':<15} {airstream_2.rho:.3f}{'':<15}",
            f"{ 'Spes. varmekap. [J/kgK]':<30} {airstream_1.cp:.1f}{'':<15} {airstream_2.cp:.1f}{'':<15}"
        ])

    @staticmethod
    def print_air_properties(airstream_1: 'AirStream', airstream_2: 'AirStream') -> None:
        print(Report.get_air_properties_string(airstream_1, airstream_2))

    @staticmethod
    def get_flow_parameters_string(state, airstream_1: 'AirStream', airstream_2: 'AirStream') -> str:
        return "\n".join([
            f"\n{'STRØMNINGSPARAMETRE':^90}",
            "-"*90,
            f"{ 'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}",
            "-"*90,
            f"{ 'Massestrøm [kg/s]':<30} {airstream_1.m_dot if airstream_1 else 0:<25.3f} {airstream_2.m_dot if airstream_2 else 0:<25.3f}",
            f"{ 'Volumstrøm [m³/s]':<30} {state.q_vol_1 if state.q_vol_1 is not None else 0:.3f}{'':<15} {state.q_vol_2 if state.q_vol_2 is not None else 0:.3f}{'':<15}",
            f"{ 'Volumstrøm [m³/h]':<30} {(state.q_vol_1*3600) if state.q_vol_1 is not None else 0:.1f}{'':<15} {(state.q_vol_2*3600) if state.q_vol_2 is not None else 0:.1f}{'':<15}",
            f"{ 'Lufthastighet [m/s]':<30} {state.v_1 if state.v_1 is not None else 0:.2f}{'':<15} {state.v_2 if state.v_2 is not None else 0:.2f}{'':<15}",
            f"{ 'Massestrømhastighet [kg/m²s]':<30} {state.g_1 if state.g_1 is not None else 0:.1f}{'':<15} {state.g_2 if state.g_2 is not None else 0:.1f}{'':<15}",
            f"{ 'Reynolds tall':<30} {state.re_1 if state.re_1 is not None else 0:.0f}{'':<15} {state.re_2 if state.re_2 is not None else 0:.0f}{'':<15}",
            f"{ 'Strømningsregime':<30} {state.flow_regime_1 if state.flow_regime_1 is not None else '':<25} {state.flow_regime_2 if state.flow_regime_2 is not None else '':<25}",
            f"{ 'Nusselt tall':<30} {state.nu_1 if state.nu_1 is not None else 0:.2f}{'':<15} {state.nu_2 if state.nu_2 is not None else 0:.2f}{'':<15}",
            f"{ 'Varmeovergangstall [W/m²K]':<30} {state.h_1 if state.h_1 is not None else 0:.2f}{'':<15} {state.h_2 if state.h_2 is not None else 0:.2f}{'':<15}",
            f"{ 'Trykkfall [Pa]':<30} {state.delta_p_1 if state.delta_p_1 is not None else 0:.1f}{'':<15} {state.delta_p_2 if state.delta_p_2 is not None else 0:.1f}{'':<15}",
            f"{ 'Trykkfall [kPa]':<30} {(state.delta_p_1/1000) if state.delta_p_1 is not None else 0:.3f}{'':<15} {(state.delta_p_2/1000) if state.delta_p_2 is not None else 0:.3f}{'':<15}",
            f"{ 'Friksjonsfaktor':<30} {state.f_1 if state.f_1 is not None else 0:.4f}{'':<15} {state.f_2 if state.f_2 is not None else 0:.4f}{'':<15}",
            f"{ 'Oppholdstid [s]':<30} {state.t_res_1 if state.t_res_1 is not None else 0:.2f}{'':<15} {state.t_res_2 if state.t_res_2 is not None else 0:.2f}{'':<15}"
        ])

    @staticmethod
    def print_flow_parameters(state, airstream_1: 'AirStream', airstream_2: 'AirStream') -> None:
        print(Report.get_flow_parameters_string(state, airstream_1, airstream_2))

    @staticmethod
    def get_inlet_conditions_string(airstream_1: 'AirStream', airstream_2: 'AirStream') -> str:
        return "\n".join([
            f"\n{'INNLØPSBETINGELSER':^90}",
            "-"*90,
            f"{ 'Parameter':<30} {'Varm Side':<25} {'Kald Side':<25}",
            "-"*90,
            f"{ 'Innløpstemperatur [°C]':<30} {airstream_1.temperature_c:<25.1f} {airstream_2.temperature_c:<25.1f}",
            f"{ 'Relativ fuktighet [%]':<30} {airstream_1.phi*100:<25.1f} {airstream_2.phi*100:<25.1f}"
        ])

    @staticmethod
    def print_inlet_conditions(airstream_1: 'AirStream', airstream_2: 'AirStream') -> None:
        print(Report.get_inlet_conditions_string(airstream_1, airstream_2))

    @staticmethod
    def get_thermal_resistances_string(state) -> str:
        return "\n".join([
            f"\n{'VARMEMOTSTANDER':^90}",
            "-"*90,
            f"{ 'Type':<30} {'Verdi [K/W]':<25} {'Kommentar':<25}",
            "-"*90,
            f"{ 'Konvektivt varmeovergangstall side 1':<30} {state.r_conv_1:.6f}{'':<15} {'Varm side':<25}",
            f"{ 'Konvektivt varmeovergangstall side 2':<30} {state.r_conv_2:.6f}{'':<15} {'Kald side':<25}",
            f"{ 'Konduktiv varmemotstand plate':<30} {state.r_cond:.6f}{'':<15} {'Plate':<25}",
            f"{ 'Total motstand':<30} {state.r_total:.6f}{'':<15} {'Sum':<25}"
        ])

    @staticmethod
    def print_thermal_resistances(state) -> None:
        print(Report.get_thermal_resistances_string(state))

    @staticmethod
    def get_results_summary_string(state, exchanger: 'PlateHeatExchanger') -> str:
        return "\n".join([
            f"\n{'RESULTATER':^90}",
            "-"*90,
            f"{ 'Total U-verdi:':<30} {state.u_value:.2f} W/m²K",
            f"{ 'Total varmeoverflate:':<30} {exchanger.area_heat_total:.2f} m²",
            f"{ 'NTU:':<30} {state.ntu:.2f}",
            f"{ 'C_min/C_max:':<30} {state.c_min/state.c_max:.3f}",
            f"{ 'Effektivitet:':<30} {state.effectiveness*100:.1f} %",
            f"{ 'Maks varmeoverføring:':<30} {state.q_max/1000:.2f} kW",
            f"{ 'Faktisk varmeoverføring:':<30} {state.q_actual/1000:.2f} kW"
        ])

    @staticmethod
    def print_results_summary(state, exchanger: 'PlateHeatExchanger') -> None:
        print(Report.get_results_summary_string(state, exchanger))
        
    @staticmethod
    def get_report_string(
        exchanger,
        state,
        airstream_1: 'AirStream',
        airstream_2: 'AirStream',
        flow_arrangement: "FlowArrangement"
    ) -> str:
        """
        Genererer en rapport som en streng ved å kalle get-metodene.
        """
        report_parts = [
            Report.get_input_summary_string(airstream_1, airstream_2, exchanger),
            Report.get_header_string(flow_arrangement),
            Report.get_geometry_string(exchanger),
            Report.get_air_properties_string(airstream_1, airstream_2),
            Report.get_flow_parameters_string(state, airstream_1, airstream_2),
            Report.get_inlet_conditions_string(airstream_1, airstream_2),
            Report.get_thermal_resistances_string(state),
            Report.get_results_summary_string(state, exchanger),
            "\n" + "="*90
        ]
        return "\n".join(report_parts)

    @staticmethod
    def print_all(
        exchanger,
        state,
        airstream_1: 'AirStream',
        airstream_2: 'AirStream',
        flow_arrangement: "FlowArrangement"
    ) -> None:
        """
        Skriver ut resultater i tabellform med to kolonner.
        Deler opp utskriften i mindre metoder for bedre oversikt og utvidbarhet.
        """
        print(Report.get_report_string(exchanger, state, airstream_1, airstream_2, flow_arrangement))