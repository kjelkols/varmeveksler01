from typing import Protocol, Type
from pydantic import BaseModel
from moistair import AirStreamInputModel, AirStreamModel, AirStream
from flowcorrelations import FLowInputModel, FlowResults

class SimulationProtocol(Protocol):
    input_model: Type[BaseModel]
    output_model: Type[BaseModel]
    name: str
    description: str

    def run(self, input_data: BaseModel) -> BaseModel: ...
    def report(self, input_data: BaseModel, output_data: BaseModel, format: str = "html") -> str: ...

class MoistAirSimulation:
    input_model = AirStreamInputModel
    output_model = AirStreamModel
    name = "Fuktig luft"
    description = "Beregning av luftens egenskaper ved gitt tilstand."

    def run(self, input_data: BaseModel) -> BaseModel:
        # Typecasting: Vi validerer og konverterer input_data til riktig Pydantic-modell (AirStreamInputModel)
        data = AirStreamInputModel.model_validate(input_data)
        air_stream = AirStream.from_dict(data.model_dump())
        return air_stream.to_pydantic()

    def report(self, input_data: BaseModel, output_data: BaseModel, format: str = "html") -> str:
        # Typecasting: Vi validerer og konverterer input_data og output_data til riktige Pydantic-modeller
        data = AirStreamInputModel.model_validate(input_data)
        result = AirStreamModel.model_validate(output_data)
        if format == "html":
            return f"""
            <h3>Detaljert rapport for fuktig luft</h3>
            <p>Beregning for {data.temperature_c} °C, {data.relative_humidity*100:.1f}% RH, {data.pressure} Pa.</p>
            <ul>
              <li>Tetthet: {result.density:.3f} kg/m³</li>
              <li>Entalpi: {result.enthalpy:.0f} J/kg</li>
              <li>Duggpunkt: {result.dew_point:.2f} °C</li>
              <li>Spesifikk varmekapasitet: {result.specific_heat_capacity:.1f} J/kgK</li>
              <li>Fuktighetsforhold: {result.humidity_ratio:.5f} kg/kg</li>
              <li>Prandtl-tall: {result.prandtl_number:.3f}</li>
              <li>Dynamisk viskositet: {result.dynamic_viscosity:.6e} Pa·s</li>
              <li>Termisk konduktivitet: {result.thermal_conductivity:.4f} W/mK</li>
            </ul>
            """
        elif format == "markdown":
            return (
                f"### Detaljert rapport for fuktig luft\n"
                f"- Temperatur: {data.temperature_c} °C\n"
                f"- Relativ fuktighet: {data.relative_humidity*100:.1f}%\n"
                f"- Trykk: {data.pressure} Pa\n"
                f"- **Tetthet:** {result.density:.3f} kg/m³\n"
                f"- **Entalpi:** {result.enthalpy:.0f} J/kg\n"
                f"- **Duggpunkt:** {result.dew_point:.2f} °C\n"
                f"- **Spesifikk varmekapasitet:** {result.specific_heat_capacity:.1f} J/kgK\n"
                f"- **Fuktighetsforhold:** {result.humidity_ratio:.5f} kg/kg\n"
                f"- **Prandtl-tall:** {result.prandtl_number:.3f}\n"
                f"- **Dynamisk viskositet:** {result.dynamic_viscosity:.6e} Pa·s\n"
                f"- **Termisk konduktivitet:** {result.thermal_conductivity:.4f} W/mK\n"
            )
        else:
            return str(result)

class AirflowSimulation:
    input_model = FLowInputModel
    output_model = FlowResults
    name = "Luftstrøm"
    description = "Beregning av luftens egenskaper i en strømning."

    def run(self, input_data: BaseModel) -> BaseModel:
        data = FLowInputModel.model_validate(input_data)
        air_stream = AirStream.from_dict(data.model_dump())
        return air_stream.to_pydantic()

    def report(self, input_data: BaseModel, output_data: BaseModel, format: str = "html") -> str:
        data = FLowInputModel.model_validate(input_data)
        result = FlowResults.model_validate(output_data)
        if format == "html":
            return f"""
            <h3>Rapport for luftstrøm</h3>
            <p>Beregning for {data.mass_flow_rate} kg/s, {data.density*100:.1f} kg/m³, {data.pressure} Pa.</p>
            <ul>
              <li>Reynolds number: {result.reynolds_number:.3f} kg/m³</li>
              <li>Prandtl-tall: {result.prandtl_number:.3f}</li>
            </ul>
            """
        elif format == "markdown":
            return (
                f"### Rapport for luftstrøm\n"
            )
        else:
            return str(result)