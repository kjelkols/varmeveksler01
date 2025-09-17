
from flowcorrelations import flow_side_results
import math
from typing import TYPE_CHECKING
from models import HeatExchangerParameters, HeatExchangerResults
from definitions import FlowArrangement

if TYPE_CHECKING:
    from moistair import AirStream

class PlateHeatExchanger:
    def __init__(
        self,
        width: float,
        length: float,
        plate_thickness: float,
        thermal_conductivity_plate: float,
        number_of_plates: int,
        channel_height: float
    ) -> None:
        # Geometriske parametre
        self.width = width          # Bredde [m]
        self.length = length         # Lengde [m]
        self.plate_thickness = plate_thickness  # Platetykkelse [m]
        self.thermal_conductivity_plate = thermal_conductivity_plate   # Varmeledningsevne plate [W/mK]
        self.number_of_plates = number_of_plates           # Antall plater (starter med stor N)
        self.channel_height = channel_height  # Kanalhøyde [m] (typisk verdi)

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
    def area_flow_1(self) -> float:
        return self.width * self.channel_height * self.number_of_channels_side_1
    @property
    def area_flow_2(self) -> float:
        return self.width * self.channel_height * self.number_of_channels_side_2
    @property
    def volume_channel(self) -> float:
        return self.width * self.length * self.channel_height * (self.number_of_plates - 1)
    @property
    def volume_total_1(self) -> float:
        return self.volume_channel * (self.number_of_channels_side_1 / (self.number_of_channels_side_1 + self.number_of_channels_side_2))
    @property
    def volume_total_2(self) -> float:
        return self.volume_channel * (self.number_of_channels_side_2 / (self.number_of_channels_side_1 + self.number_of_channels_side_2))
    # ...eksisterende kode for volume_channel og volume_total_1 finnes lenger ned...
    @property
    def hydraulic_diameter(self) -> float:
        return 2 * (self.width * self.channel_height) / (self.width + self.channel_height)
    @property
    def area_plate(self) -> float:
        return 2 * self.width * self.length

    def calculate_parameters(
        self,
        airstream_1: 'AirStream',
        airstream_2: 'AirStream'
    ) -> HeatExchangerParameters:
        """
        Beregner og returnerer et HeatExchangerParameters-objekt for gitte luftstrømmer.
        """
        side1 = flow_side_results(
            mass_flow_rate=airstream_1.m_dot,
            density=airstream_1.rho,
            dynamic_viscosity=airstream_1.dynamic_viscosity,
            specific_heat_capacity=airstream_1.cp,
            thermal_conductivity=airstream_1.k,
            flow_area=self.area_flow_1,
            hydraulic_diameter=self.hydraulic_diameter,
            length=self.length
        )
        side2 = flow_side_results(
            mass_flow_rate=airstream_2.m_dot,
            density=airstream_2.rho,
            dynamic_viscosity=airstream_2.dynamic_viscosity,
            specific_heat_capacity=airstream_2.cp,
            thermal_conductivity=airstream_2.k,
            flow_area=self.area_flow_2,
            hydraulic_diameter=self.hydraulic_diameter,
            length=self.length
        )
        h_1 = side1["heat_transfer_coefficient"]
        h_2 = side2["heat_transfer_coefficient"]
        area_heat_1 = self.area_heat_1
        area_heat_2 = self.area_heat_2
        r_conv_1 = 1 / (h_1 * area_heat_1)
        r_conv_2 = 1 / (h_2 * area_heat_2)
        r_cond = self.plate_thickness / (self.thermal_conductivity_plate * area_heat_1)
        r_total = r_conv_1 + r_cond + r_conv_2
        u_value = 1 / (r_total * area_heat_1)
        c_1 = airstream_1.m_dot * airstream_1.cp
        c_2 = airstream_2.m_dot * airstream_2.cp
        c_min = min(c_1, c_2)
        c_max = max(c_1, c_2)
        ntu = u_value * area_heat_1 / c_min
        v_1 = side1["velocity"]
        v_2 = side2["velocity"]
        t_res_1 = self.length / v_1
        t_res_2 = self.length / v_2
        return HeatExchangerParameters(
            h_1=h_1,
            re_1=side1["reynolds_number"],
            nu_1=side1["nusselt_number"],
            v_1=v_1,
            q_vol_1=side1["volumetric_flow_rate"],
            g_1=side1["mass_flux"],
            delta_p_1=side1["pressure_drop"],
            f_1=side1["friction_factor"],
            flow_regime_1=side1["flow_regime"],
            h_2=h_2,
            re_2=side2["reynolds_number"],
            nu_2=side2["nusselt_number"],
            v_2=v_2,
            q_vol_2=side2["volumetric_flow_rate"],
            g_2=side2["mass_flux"],
            delta_p_2=side2["pressure_drop"],
            f_2=side2["friction_factor"],
            flow_regime_2=side2["flow_regime"],
            r_conv_1=r_conv_1,
            r_conv_2=r_conv_2,
            r_cond=r_cond,
            r_total=r_total,
            u_value=u_value,
            ntu=ntu,
            c_min=c_min,
            c_max=c_max,
            area_heat_1=area_heat_1,
            area_heat_2=area_heat_2,
            t_res_1=t_res_1,
            t_res_2=t_res_2
        )

    @staticmethod
    def calculate_results(
        params: HeatExchangerParameters,
        airstream_1: 'AirStream',
        airstream_2: 'AirStream',
        flow_arrangement: "FlowArrangement"
    ) -> HeatExchangerResults:
        """
        Beregner effekt, effektivitet og andre resultater basert på NTU og strømningstype.
        """
        c_r = params.c_min / params.c_max
        ntu = params.ntu
        if flow_arrangement == FlowArrangement.CROSS_FLOW:
            effectiveness = 1 - math.exp((1/c_r) * ntu**0.22 * (math.exp(-c_r * ntu**0.78) - 1))
        elif flow_arrangement == FlowArrangement.COUNTER_FLOW:
            if c_r == 1:
                effectiveness = ntu / (1 + ntu)
            else:
                numerator = 1 - math.exp(-ntu * (1 - c_r))
                denominator = 1 - c_r * math.exp(-ntu * (1 - c_r))
                effectiveness = numerator / denominator
        else:
            raise ValueError(f"Ukjent strømningsarrangement: {flow_arrangement}")
        q_max = params.c_min * abs(airstream_1.temperature_c - airstream_2.temperature_c)
        q_actual = effectiveness * q_max
        return HeatExchangerResults(
            effectiveness=effectiveness,
            q_max=q_max,
            q_actual=q_actual
        )
