from typing import Type, Any
from pydantic import BaseModel
from moistair import AirStreamInputModel, AirStreamModel, AirStream

class SimulationBase:
    input_model: Type[BaseModel]
    output_model: Type[BaseModel]
    name: str = "Generisk simulering"
    description: str = ""

    def run(self, input_data: BaseModel) -> BaseModel:
        raise NotImplementedError("Subclasses must implement the run method.")
    
    def report(self, input_data: BaseModel, output_data: BaseModel, format: str = "html") -> str:
        """
        Returnerer en rapport for simuleringen.
        format: 'html' (standard), 'markdown', evt. 'text'
        """
        # Bruk Pydantic-titler hvis tilgjengelig
        def get_titles(model):
            return {name: (field.title or name) for name, field in model.model_fields.items()}
        input_titles = get_titles(type(input_data))
        output_titles = get_titles(type(output_data))
        if format == "html":
            input_rows = "".join(f"<tr><th>{input_titles[field]}</th><td>{getattr(input_data, field)}</td></tr>" for field in input_data.model_fields)
            output_rows = "".join(f"<tr><th>{output_titles[field]}</th><td>{getattr(output_data, field)}</td></tr>" for field in output_data.model_fields)
            return f"""
            <h4>Input</h4>
            <table border=1 cellpadding=4>{input_rows}</table>
            <h4>Resultat</h4>
            <table border=1 cellpadding=4>{output_rows}</table>
            """
        elif format == "markdown":
            lines = ["### Input", "| Felt | Verdi |", "|---|---|"]
            lines += [f"| {input_titles[field]} | {getattr(input_data, field)} |" for field in input_data.model_fields]
            lines += ["", "### Resultat", "| Felt | Verdi |", "|---|---|"]
            lines += [f"| {output_titles[field]} | {getattr(output_data, field)} |" for field in output_data.model_fields]
            return "\n".join(lines)
        else:
            return str(output_data)

class MoistAirSimulation(SimulationBase):
    input_model = AirStreamInputModel
    output_model = AirStreamModel
    name = "Fuktig luft"
    description = "Beregning av luftens egenskaper ved gitt tilstand."

    def run(self, input_data: BaseModel) -> BaseModel:
        # Typecasting: Vi validerer og konverterer input_data til riktig Pydantic-modell (AirStreamInputModel)
        # Dette gir type-sikker tilgang til feltene, selv om signaturen bruker BaseModel.
        data = AirStreamInputModel.model_validate(input_data)
        air_stream = AirStream.from_dict(data.model_dump())
        return air_stream.to_pydantic()

    def report(self, input_data: BaseModel, output_data: BaseModel, format: str = "html") -> str:
        # Typecasting: Vi validerer og konverterer input_data og output_data til riktige Pydantic-modeller
        # Dette sikrer at vi kan bruke feltene med korrekt typehint og autocompletion
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
            return super().report(input_data, output_data, format)

class AirflowSimulation(SimulationBase):
    input_model = AirStreamInputModel
    output_model = AirStreamModel
    name = "Luftstrøm"
    description = "Beregning av luftens egenskaper i en strømning."

    def run(self, input_data: BaseModel) -> BaseModel:
        data = AirStreamInputModel.model_validate(input_data)
        air_stream = AirStream.from_dict(data.model_dump())
        return air_stream.to_pydantic()

    def report(self, input_data: BaseModel, output_data: BaseModel, format: str = "html") -> str:
        data = AirStreamInputModel.model_validate(input_data)
        result = AirStreamModel.model_validate(output_data)
        if format == "html":
            return f"""
            <h3>Rapport for luftstrøm</h3>
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
                f"### Rapport for luftstrøm\n"
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