import json
from flask import Flask, render_template_string, request, jsonify
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

# --- HTML-template ---
TEMPLATE = '''
<!DOCTYPE html>
<html lang="no">
<head>
    <meta charset="UTF-8">
    <title>Simulering av platevarmeveksler</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2em; background: #f9f9f9; }
        .container { max-width: 900px; margin: auto; background: #fff; padding: 2em; border-radius: 8px; box-shadow: 0 2px 8px #0001; }
        h1 { color: #0078d7; }
        .input-section, .report-section { margin-bottom: 2em; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 1em; font-size: 0.95em; }
    th, td { border: 1px solid #ccc; padding: 0.15em 0.3em; text-align: left; line-height: 1.1; }
    th { background: #f0f0f0; }
        .drop-area { border: 2px dashed #888; border-radius: 6px; background: #f9f9f9; padding: 1em; text-align: center; color: #888; margin-bottom: 1em; transition: background 0.2s, border-color 0.2s; }
        .error { color: #b00; margin-top: 1em; }
        .button-row { margin-bottom: 1em; }
        button, input[type="file"] { margin-right: 1em; }
    </style>
</head>
<body>
<div class="container">
    <h1>Simulering av platevarmeveksler</h1>
    <div class="input-section">
        <form id="input-form">
            <div class="button-row">
                <label for="json-upload" style="font-weight:bold;">Last opp inndata</label>
                <input type="file" id="json-upload" accept="application/json" style="display:none;">
                <button type="button" id="json-upload-btn">Last opp inndata</button>
                <span id="json-upload-label">(json-format)</span>
                <button type="button" id="json-download">Last ned inndata</button>
            </div>
            <div id="drop-area" class="drop-area">Dra og slipp en JSON-fil her for å laste opp</div>
            <table>
                <tr>
                    <th>Parameter</th>
                    <th>Verdi</th>
                </tr>
                {% for k in input_data['exchanger'].keys() %}
                <tr>
                    <td>{{ k }}</td>
                    <td>
                        {% if k == 'flow_arrangement' %}
                        <select name="exchanger.flow_arrangement">
                            <option value="counter-flow" {% if input_data['exchanger'][k] == 'counter-flow' %}selected{% endif %}>counter-flow</option>
                            <option value="cross-flow" {% if input_data['exchanger'][k] == 'cross-flow' %}selected{% endif %}>cross-flow</option>
                        </select>
                        {% else %}
                        <input name="exchanger.{{k}}" type="number" step="any" value="{{ input_data['exchanger'][k] }}">
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </table>
            <table>
                <tr>
                    <th>Parameter</th>
                    <th>Luftstrøm 1</th>
                    <th>Luftstrøm 2</th>
                </tr>
                {% for k in input_data['airstream_1'].keys() %}
                <tr>
                    <td>{{ k }}</td>
                    <td><input name="airstream_1.{{k}}" type="number" step="any" value="{{ input_data['airstream_1'][k] }}"></td>
                    <td><input name="airstream_2.{{k}}" type="number" step="any" value="{{ input_data['airstream_2'][k] }}"></td>
                </tr>
                {% endfor %}
            </table>
        </form>
    </div>
    <div class="report-section">
        <h2>Rapport</h2>
        <div id="report-area">{{ report_html|safe }}</div>
        <div class="error" id="error-area">{{ error|safe }}</div>
    </div>
</div>
<script>

// Tilpasset filopplasting-knapp og tekst
const uploadInput = document.getElementById('json-upload');
const uploadBtn = document.getElementById('json-upload-btn');
const uploadLabel = document.getElementById('json-upload-label');
uploadBtn.addEventListener('click', function() {
    uploadInput.click();
});
uploadInput.addEventListener('change', function() {
    if (uploadInput.files.length > 0) {
        // uploadLabel.textContent = uploadInput.files[0].name;
        uploadLabel.textContent = '(json-format)';
    } else {
        uploadLabel.textContent = '(json-format)';
    }
});


// Filopplasting via input
document.getElementById('json-upload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const data = JSON.parse(e.target.result);
            fetch('/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(r => r.json())
            .then(obj => {
                if (obj.error) {
                    document.getElementById('error-area').textContent = obj.error;
                } else {
                    document.getElementById('error-area').textContent = '';
                    // Oppdater skjema med gyldige verdier fra fil
                    for (const section of ['airstream_1', 'airstream_2', 'exchanger']) {
                        if (!data[section]) continue;
                        for (const key in data[section]) {
                            const input = document.querySelector(`[name="${section}.${key}"]`);
                            if (input) input.value = data[section][key];
                        }
                    }
                    updateReport();
                }
            });
        } catch (err) {
            const errorArea = document.getElementById('error-area');
            if (errorArea) {
                errorArea.textContent = 'Kunne ikke lese JSON: ' + err;
            } else {
                alert('Kunne ikke lese JSON: ' + err);
            }
        }
    };
    reader.readAsText(file);
});

// Nedlasting av inndata
document.getElementById('json-download').addEventListener('click', function() {
    const data = getFormData();
    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'inndata.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

// Forbedret drag-and-drop: visuell feedback og aktivering
const dropArea = document.getElementById('drop-area');
let dragCounter = 0;
document.addEventListener('dragenter', function(e) {
    e.preventDefault();
    dragCounter++;
    dropArea.style.background = '#e0e0e0';
    dropArea.style.borderColor = '#0078d7';
});
document.addEventListener('dragleave', function(e) {
    e.preventDefault();
    dragCounter--;
    if (dragCounter <= 0) {
        dropArea.style.background = '#f9f9f9';
        dropArea.style.borderColor = '#888';
    }
});
document.addEventListener('dragover', function(e) {
    e.preventDefault();
});
dropArea.addEventListener('drop', function(e) {
    e.preventDefault();
    dragCounter = 0;
    dropArea.style.background = '#f9f9f9';
    dropArea.style.borderColor = '#888';
    const file = e.dataTransfer.files[0];
    if (!file) return;
    if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
        alert('Bare JSON-filer støttes.');
        return;
    }
    const reader = new FileReader();
    reader.onload = function(ev) {
        try {
            const data = JSON.parse(ev.target.result);
            for (const section of ['airstream_1', 'airstream_2', 'exchanger']) {
                if (!data[section]) continue;
                for (const key in data[section]) {
                    const input = document.querySelector(`[name="${section}.${key}"]`);
                    if (input) input.value = data[section][key];
                }
            }
            updateReport();
        } catch (err) {
            alert('Kunne ikke lese JSON: ' + err);
        }
    };
    reader.readAsText(file);
});

function getFormData() {
    const form = document.getElementById('input-form');
    const data = { airstream_1: {}, airstream_2: {}, exchanger: {} };
    for (const el of form.elements) {
        if (!el.name) continue;
        const [section, key] = el.name.split('.');
        if (el.type === 'number') {
            data[section][key] = parseFloat(el.value);
        } else {
            data[section][key] = el.value;
        }
    }
    return data;
}
function updateReport() {
    const data = getFormData();
    fetch('/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(obj => {
        document.getElementById('report-area').innerHTML = obj.report_html;
        document.getElementById('error-area').innerHTML = obj.error || '';
    });
}
document.getElementById('input-form').addEventListener('input', updateReport);
window.onload = updateReport;
</script>
</body>
</html>
'''

@app.route("/", methods=["GET"])
def index():
    return render_template_string(TEMPLATE, input_data=DEFAULT_INPUT, report_html=report_html(do_simulation(DEFAULT_INPUT)), error="")

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

