import json
from flask import Flask, render_template, request, jsonify
from moistair import AirStream
from report import Report
from heatecxhanger import PlateHeatExchanger
from pydantic import ValidationError
from models import AirStreamInput, ExchangerInput, SimulationInput
from simulation_output import SimulationOutput
from heatmodels import HeatExchangerParameters, HeatExchangerResults

# --- Flask-app ---
app = Flask(__name__)

# Standard inputdata
DEFAULT_INPUT = {
    "airstream_1": {
        "mass_flow_rate": 0.5,
        "temperature_c": 80.0,
        "phi": 0.3,
        "pressure": 101325
    },
    "airstream_2": {
        "mass_flow_rate": 0.6,
        "temperature_c": 20.0,
        "phi": 0.5,
        "pressure": 101325
    },
    "exchanger": {
        "width": 1.4,
        "length": 1.4,
        "plate_thickness": 0.0005,
        "thermal_conductivity_plate": 15.0,
        "number_of_plates": 30,
        "channel_height": 0.005,
        "flow_arrangement": "counter-flow"
    }
}

# --- Simuleringsfunksjon ---
def do_simulation(input_data: dict) -> SimulationOutput:
    validated = SimulationInput(**input_data)
    airstream_1 = AirStream.from_dict(validated.airstream_1.model_dump())
    airstream_2 = AirStream.from_dict(validated.airstream_2.model_dump())
    phex = PlateHeatExchanger(**validated.exchanger.model_dump())
    params = phex.calculate_parameters(airstream_1, airstream_2)
    results = PlateHeatExchanger.calculate_results(params, airstream_1, airstream_2, phex.flow_arrangement)
    return SimulationOutput(
        airstream_1=validated.airstream_1,
        airstream_2=validated.airstream_2,
        exchanger=validated.exchanger,
        parameters=params,
        results=results
    )

# --- Rapport som HTML ---
def report_html(result: SimulationOutput) -> str:
    airstream_1 = AirStream.from_dict(result.airstream_1.model_dump())
    airstream_2 = AirStream.from_dict(result.airstream_2.model_dump())
    phex = PlateHeatExchanger(**result.exchanger.model_dump())
    # Kombiner parametre og resultater til én state-aktig objekt for rapporten
    state = type('HeatExchangerState', (), {})()
    for k, v in result.parameters.model_dump().items():
        setattr(state, k, v)
    for k, v in result.results.model_dump().items():
        setattr(state, k, v)
    import io, sys
    buf = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buf
    Report.print_all(phex, state, airstream_1, airstream_2)
    sys.stdout = sys_stdout
    return f"<pre>{buf.getvalue()}</pre>"

@app.route("/", methods=["GET"])
def index():
    return render_template(
        "webapp.html",
        input_data=DEFAULT_INPUT,
        report_html=report_html(do_simulation(DEFAULT_INPUT)),
        error=""
    )

@app.route("/simulate", methods=["POST"])
def simulate():
    try:
        input_data = request.get_json()
        result = do_simulation(input_data)
        return jsonify({"report_html": report_html(result), "error": ""})
    except ValidationError as e:
        return jsonify({"report_html": "", "error": e.json()})
    except Exception as e:
        return jsonify({"report_html": "", "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)


