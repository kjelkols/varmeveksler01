from typing import Any, Dict
from pydantic import BaseModel, Field
import math

class AirStreamInputModel(BaseModel):
    mass_flow_rate: float = Field(
        ..., ge=0, title="Masseflow (kg/s)", description="Må være >= 0"
    )
    temperature_c: float = Field(
        ..., ge=-100, le=100, title="Temperatur (°C)", description="Typisk -100 til 100"
    )
    relative_humidity: float = Field(
        ..., ge=0, le=1, title="Relativ fuktighet (0-1)", description="0 = tørr, 1 = mettet"
    )
    pressure: float = Field(
        ..., ge=50000, le=200000, title="Trykk (Pa)", description="Typisk 50 000 til 200 000"
    )

class AirStreamModel(BaseModel):
    mass_flow_rate: float = Field(..., title="Masseflow (kg/s)")
    temperature_c: float = Field(..., title="Temperatur (°C)")
    relative_humidity: float = Field(..., title="Relativ fuktighet (0-1)")
    pressure: float = Field(..., title="Trykk (Pa)")
    density: float = Field(..., title="Tetthet (kg/m³)")
    dynamic_viscosity: float = Field(..., title="Dynamisk viskositet (Pa·s)")
    specific_heat_capacity: float = Field(..., title="Spesifikk varmekapasitet (J/kgK)")
    thermal_conductivity: float = Field(..., title="Termisk konduktivitet (W/mK)")
    prandtl_number: float = Field(..., title="Prandtl-tall")
    enthalpy: float = Field(..., title="Entalpi (J/kg)")
    humidity_ratio: float = Field(..., title="Fuktighetsforhold (kg/kg)")
    dew_point: float = Field(..., title="Duggpunkt (°C)")

class AirProperties:
    """Beregner og lagrer luftens egenskaper ut fra temperatur, relativ fuktighet og trykk."""
    R: float = 287.05  # Gasskonstant for tørr luft [J/kgK]
    MU_REF: float = 1.716e-5  # Referanseviskositet [Pa·s]
    T0: float = 273.15  # Referansetemperatur [K]
    S: float = 110.4    # Sutherlandkonstant [K]
    R_v: float = 461.5  # Gasskonstant for vanndamp [J/kgK]
    P_WS_0: float = 610.94  # Referansedamptrykk [Pa]
    TETENS_A: float = 17.625
    TETENS_B: float = 243.04

    def __init__(self, temperature_c: float, relative_humidity: float, pressure: float) -> None:
        """
        Parameters:
            temperature_c: Temperatur i Celsius
            relative_humidity: Relativ fuktighet (0-1)
            pressure: Trykk i Pa
        """
        self.temperature_c: float = temperature_c
        self.relative_humidity: float = relative_humidity
        self.pressure: float = pressure
        self.density: float = float("nan")
        self.dynamic_viscosity: float = float("nan")
        self.specific_heat_capacity: float = float("nan")
        self.thermal_conductivity: float = float("nan")
        self.prandtl_number: float = float("nan")
        self.enthalpy: float = float("nan")
        self.humidity_ratio: float = float("nan")
        self.dew_point: float = float("nan")
        self._calculate()

    @staticmethod
    def from_temp_pressure_x(temperature_c: float, pressure: float, humidity_ratio: float) -> 'AirProperties':
        """
        Opprett AirProperties fra temperatur (C), trykk (Pa) og fuktighetsforhold (kg vanndamp/kg tørr luft).
        Beregner relativ fuktighet ut fra x, temperatur og trykk.
        """
        p_ws = AirProperties.P_WS_0 * (2.718281828459045 ** (AirProperties.TETENS_A * temperature_c / (AirProperties.TETENS_B + temperature_c)))
        p_da = pressure / (1 + 1.6078 * humidity_ratio)
        p_w = pressure - p_da
        relative_humidity = p_w / p_ws if p_ws > 0 else 0.0
        return AirProperties(temperature_c=temperature_c, relative_humidity=relative_humidity, pressure=pressure)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AirProperties':
        """Lag AirProperties fra dict eller Pydantic-modell."""
        return AirProperties(
            temperature_c=data["temperature_c"],
            relative_humidity=data["relative_humidity"],
            pressure=data["pressure"]
        )

    @staticmethod
    def calc_saturation_vapor_pressure(temperature_c: float) -> float:
        """Beregner metningsdamptrykk (Pa) ved gitt temperatur (Celsius)."""
        return AirProperties.P_WS_0 * (2.718281828459045 ** (AirProperties.TETENS_A * temperature_c / (AirProperties.TETENS_B + temperature_c)))

    @staticmethod
    def calc_vapor_partial_pressure(relative_humidity: float, p_ws: float) -> float:
        """Beregner partialtrykk for vanndamp (Pa)."""
        return relative_humidity * p_ws

    @staticmethod
    def calc_humidity_ratio(p_w: float, pressure: float) -> float:
        """Beregner fuktighetsforhold (kg vanndamp/kg tørr luft)."""
        p_da = pressure - p_w
        return 0.622 * p_w / p_da

    @staticmethod
    def calc_density(pressure: float, temperature_c: float, x: float) -> float:
        """Beregner tetthet (kg/m³) for fuktig luft."""
        T_k = temperature_c + 273.15
        return pressure / (AirProperties.R * T_k * (1 + 1.6078 * x))

    @staticmethod
    def calc_dynamic_viscosity(temperature_c: float) -> float:
        """Beregner dynamisk viskositet (Pa·s) for tørr luft."""
        T_k = temperature_c + 273.15
        return AirProperties.MU_REF * ((AirProperties.T0 + AirProperties.S) / (T_k + AirProperties.S)) * ((T_k / AirProperties.T0) ** 1.5)

    @staticmethod
    def calc_specific_heat_capacity(x: float) -> float:
        """Beregner spesifikk varmekapasitet (J/kgK) for fuktig luft."""
        cp_da = 1005.0
        cp_v = 1860.0
        return cp_da * (1 - x) + cp_v * x

    @staticmethod
    def calc_thermal_conductivity(temperature_c: float) -> float:
        """Beregner termisk konduktivitet (W/mK) for tørr luft (tilnærming)."""
        return 0.024 + 0.00007 * temperature_c

    @staticmethod
    def calc_prandtl_number(temperature_c: float) -> float:
        """Beregner Prandtl-tall for tørr luft (tilnærming)."""
        return 0.7 + 0.0002 * temperature_c

    @staticmethod
    def calc_enthalpy(temperature_c: float, x: float) -> float:
        """Beregner entalpi (J/kg tørr luft) for fuktig luft."""
        cp_da = 1005.0
        h_da = cp_da * temperature_c
        h_v = 2501000 + 1860 * temperature_c
        return h_da + x * h_v

    @staticmethod
    def calc_dew_point(p_w: float) -> float:
        """Beregner duggpunkt (°C) fra partialtrykk vanndamp (Pa)."""
        if p_w > 0:
            a = AirProperties.TETENS_A
            b = AirProperties.TETENS_B
            return b * (math.log(p_w / AirProperties.P_WS_0)) / (a - math.log(p_w / AirProperties.P_WS_0))
        return float("nan")

    def _calculate(self) -> None:
        """Beregn og sett luftens egenskaper som attributter, inkl. fuktig luft og entalpi."""
        p_ws = self.calc_saturation_vapor_pressure(self.temperature_c)
        p_w = self.calc_vapor_partial_pressure(self.relative_humidity, p_ws)
        x = self.calc_humidity_ratio(p_w, self.pressure)
        self.humidity_ratio = x
        self.density = self.calc_density(self.pressure, self.temperature_c, x)
        self.dynamic_viscosity = self.calc_dynamic_viscosity(self.temperature_c)
        self.specific_heat_capacity = self.calc_specific_heat_capacity(x)
        self.thermal_conductivity = self.calc_thermal_conductivity(self.temperature_c)
        self.prandtl_number = self.calc_prandtl_number(self.temperature_c)
        self.enthalpy = self.calc_enthalpy(self.temperature_c, x)
        self.dew_point = self.calc_dew_point(p_w)

class AirStream:
    """Representerer en luftstrøm med masseflow og luftegenskaper."""
    def __init__(self, mass_flow_rate: float, air_properties: AirProperties) -> None:
        self.mass_flow_rate: float = mass_flow_rate
        self.air: AirProperties = air_properties

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AirStream':
        """Lag AirStream fra dict eller AirStreamInputModel."""
        return AirStream(
            mass_flow_rate=data["mass_flow_rate"],
            air_properties=AirProperties.from_dict(data)
        )

    def to_pydantic(self) -> AirStreamModel:
        """Returner alle relevante verdier som Pydantic-modell."""
        return AirStreamModel(
            mass_flow_rate=self.mass_flow_rate,
            temperature_c=self.temperature_c,
            relative_humidity=self.relative_humidity,
            pressure=self.pressure,
            density=self.density,
            dynamic_viscosity=self.dynamic_viscosity,
            specific_heat_capacity=self.specific_heat_capacity,
            thermal_conductivity=self.thermal_conductivity,
            prandtl_number=self.prandtl_number,
            enthalpy=self.enthalpy,
            humidity_ratio=self.humidity_ratio,
            dew_point=self.dew_point
        )

    @property
    def temperature_c(self) -> float:
        """Temperatur i Celsius for denne strømmen."""
        return self.air.temperature_c

    @property
    def relative_humidity(self) -> float:
        """Relativ fuktighet (0-1) for denne strømmen."""
        return self.air.relative_humidity

    @property
    def pressure(self) -> float:
        """Trykk (Pa) for denne strømmen."""
        return self.air.pressure

    @property
    def density(self) -> float:
        """Tetthet (kg/m³) for denne strømmen."""
        return self.air.density

    @property
    def dynamic_viscosity(self) -> float:
        """Dynamisk viskositet (Pa·s) for denne strømmen."""
        return self.air.dynamic_viscosity

    @property
    def specific_heat_capacity(self) -> float:
        """Spesifikk varmekapasitet (J/kgK) for denne strømmen."""
        return self.air.specific_heat_capacity

    @property
    def thermal_conductivity(self) -> float:
        """Termisk konduktivitet (W/mK) for denne strømmen."""
        return self.air.thermal_conductivity

    @property
    def prandtl_number(self) -> float:
        """Prandtl-tall for denne strømmen."""
        return self.air.prandtl_number

    @property
    def enthalpy(self) -> float:
        """Spesifikk entalpi (J/kg tørr luft) for denne strømmen."""
        return self.air.enthalpy

    @property
    def humidity_ratio(self) -> float:
        """Fuktighetsforhold (kg vanndamp/kg tørr luft) for denne strømmen."""
        return self.air.humidity_ratio

    @property
    def dew_point(self) -> float:
        """Duggpunkt (°C) for denne strømmen."""
        return self.air.dew_point

if __name__ == "__main__":  
    """Eksempel på bruk av AirStreamInputModel som input og AirStream/AirStreamModel for resultat.
    Sammenligner med reelle verdier for fuktig luft (kilde: standardtabeller)."""
    # Typisk eksempel: 25°C, 50% RH, 101325 Pa
    input_data = AirStreamInputModel(
        mass_flow_rate=1.2,
        temperature_c=25,
        relative_humidity=0.5,
        pressure=101325
    )
    air_stream = AirStream.from_dict(input_data.model_dump())
    result = air_stream.to_pydantic()
    print(f"Mass flow rate: {result.mass_flow_rate} kg/s")
    print(f"Temperature: {result.temperature_c} °C")
    print(f"Density: {result.density:.3f} kg/m³ (tabell: ~1.184)")
    print(f"Dynamic Viscosity: {result.dynamic_viscosity:.6e} Pa·s (tabell: ~1.85e-5)")
    print(f"Specific Heat Capacity: {result.specific_heat_capacity:.1f} J/(kg·K) (tabell: ~1007)")
    print(f"Thermal Conductivity: {result.thermal_conductivity:.4f} W/(m·K) (tabell: ~0.026)")
    print(f"Prandtl Number: {result.prandtl_number:.3f} (tabell: ~0.707)")
    print(f"Enthalpy: {result.enthalpy:.0f} J/kg (tabell: ~50200)")
    print(f"Humidity Ratio: {result.humidity_ratio:.5f} kg/kg (tabell: ~0.0098)")
    print(f"Dew Point: {result.dew_point:.2f} °C (tabell: ~13.9)")