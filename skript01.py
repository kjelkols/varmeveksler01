from pydantic import ValidationError
from moistair import AirStream
from report import Report
from heatecxhanger import PlateHeatExchanger
from models import AirStreamInput, ExchangerInput, SimulationInput, SimulationResult
from heatmodels import HeatExchangerParameters, HeatExchangerResults
from simulation_output import SimulationOutput

def do_simulation(input_data: SimulationInput) -> SimulationOutput:
    """
    Tar inn input-data som Pydantic-objekt, returnerer resultater som Pydantic-objekt.
    Kaster ValidationError hvis input er ugyldig.
    """
    airstream_1 = AirStream.from_dict(input_data.airstream_1.model_dump())
    airstream_2 = AirStream.from_dict(input_data.airstream_2.model_dump())
    phex = PlateHeatExchanger(**input_data.exchanger.model_dump())
    params = phex.calculate_parameters(airstream_1, airstream_2)
    results = PlateHeatExchanger.calculate_results(params, airstream_1, airstream_2, phex.flow_arrangement)
    return SimulationOutput(
        airstream_1=input_data.airstream_1,
        airstream_2=input_data.airstream_2,
        exchanger=input_data.exchanger,
        parameters=params,
        results=results
    )

def print_report(result: SimulationOutput) -> None:
    """Skriver ut rapport basert på SimulationOutput fra do_simulation."""
    airstream_1 = AirStream.from_dict(result.airstream_1.model_dump())
    airstream_2 = AirStream.from_dict(result.airstream_2.model_dump())
    phex = PlateHeatExchanger(**result.exchanger.model_dump())
    # Kombiner parametre og resultater til én state-aktig objekt for rapporten
    state = type('HeatExchangerState', (), {})()
    for k, v in result.parameters.model_dump().items():
        setattr(state, k, v)
    for k, v in result.results.model_dump().items():
        setattr(state, k, v)
    Report.print_all(phex, state, airstream_1, airstream_2)

# Kjør en eksampelberegning
if __name__ == "__main__":
    # Samle alle inputdata i ett Pydantic-objekt
    input_data = SimulationInput(
        airstream_1=AirStreamInput(
            mass_flow_rate=0.5,
            temperature_c=80.0,
            phi=0.3,
            pressure=101325
        ),
        airstream_2=AirStreamInput(
            mass_flow_rate=0.6,
            temperature_c=20.0,
            phi=0.5,
            pressure=101325
        ),
        exchanger=ExchangerInput(
            width=1.4,
            length=1.4,
            plate_thickness=0.0005,
            thermal_conductivity_plate=15.0,
            number_of_plates=30,
            channel_height=0.005,
            flow_arrangement="counter-flow"
        )
    )

    try:
        result = do_simulation(input_data)
        print(result.model_dump_json(indent=2))
        # For å skrive rapport til skjerm, bruk:
        print_report(result)
    except ValidationError as e:
        print("Input validation error:")
        print(e.json())
