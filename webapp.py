import json
from flask import Flask, render_template, request, jsonify
from moistair import AirStream
from report import Report
from heatecxhanger import PlateHeatExchanger, FlowArrangement
from pydantic import ValidationError
from models import SimulationInput
from simulation_output import SimulationOutput

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
        "channel_height": 0.005
    },
    "flow_arrangement": "counter-flow"
}

# --- Simuleringsfunksjon ---
def do_simulation(input_data: dict) -> SimulationOutput:
    validated = SimulationInput(**input_data)
    airstream_1 = AirStream.from_dict(validated.airstream_1.model_dump())
    airstream_2 = AirStream.from_dict(validated.airstream_2.model_dump())
    
    exchanger_data = validated.exchanger.model_dump()
    phex = PlateHeatExchanger(**exchanger_data)
    params = phex.calculate_parameters(airstream_1, airstream_2)
    
    results = PlateHeatExchanger.calculate_results(
        params, 
        airstream_1, 
        airstream_2, 
        validated.flow_arrangement
    )
    
    return SimulationOutput(
        airstream_1=validated.airstream_1,
        airstream_2=validated.airstream_2,
        exchanger=validated.exchanger,
        parameters=params,
        results=results
    )

# --- Rapport som HTML ---
def report_html(result: SimulationOutput, flow_arrangement: FlowArrangement) -> str:
    airstream_1 = AirStream.from_dict(result.airstream_1.model_dump())
    airstream_2 = AirStream.from_dict(result.airstream_2.model_dump())
    
    exchanger_data = result.exchanger.model_dump()
    phex = PlateHeatExchanger(**exchanger_data)
    
    # Kombiner parametre og resultater til én state-aktig objekt for rapporten
    state = type('HeatExchangerState', (), {})()
    for k, v in result.parameters.model_dump().items():
        setattr(state, k, v)
    for k, v in result.results.model_dump().items():
        setattr(state, k, v)
    
    report_string = Report.get_report_string(phex, state, airstream_1, airstream_2, flow_arrangement)
    return f"<pre>{report_string}</pre>"

@app.route("/", methods=["GET"])
def index():
    try:
        simulation_result = do_simulation(DEFAULT_INPUT)
        # The flow arrangement is now at the top level of the input data
        flow_arrangement_from_input = FlowArrangement(DEFAULT_INPUT["flow_arrangement"])
        report = report_html(simulation_result, flow_arrangement_from_input)
        error = ""
    except ValidationError as e:
        report = ""
        error = e.json()
    except Exception as e:
        report = ""
        error = str(e)
        
    return render_template(
        "webapp.html",
        input_data=DEFAULT_INPUT,
        report_html=report,
        error=error
    )

@app.route("/simulate", methods=["POST"])
def simulate():
    try:
        input_data = request.get_json()
        result = do_simulation(input_data)
        flow_arrangement_from_input = FlowArrangement(input_data["flow_arrangement"])
        return jsonify({"report_html": report_html(result, flow_arrangement_from_input), "error": ""})
    except ValidationError as e:
        return jsonify({"report_html": "", "error": e.json()})
    except Exception as e:
        return jsonify({"report_html": "", "error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)