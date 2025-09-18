from flask import Flask, request, render_template
from app.mysimulator import MySimulator1, MySimulator2
import json
import html as _html_escape

app = Flask(__name__)
app.secret_key = 'dev'

# Registrer alle simulator-klasser her (stateless)
SIMULATORS = {
    "add": MySimulator1,
    "mult": MySimulator2,
    # "annen": AnnenSimulator,
}


@app.route('/', methods=['GET', 'POST'])
def index():
    # ...existing code...
    # Finn valgt simulator
    if request.method == 'POST':
        selected_simulator_key = request.form.get('simulator', list(SIMULATORS.keys())[0])
        prev_sim = request.form.get('prev_sim', selected_simulator_key)
        sim_class = SIMULATORS[selected_simulator_key]
        input_model = sim_class.input_model
        if selected_simulator_key != prev_sim:
            input_data = input_model()
            result = None
        else:
            data = {k: v for k, v in request.form.items() if k not in ('simulator', 'prev_sim')}
            input_data = input_model(**data)
            result = sim_class.run(input_data)
    else:
        selected_simulator_key = list(SIMULATORS.keys())[0]
        sim_class = SIMULATORS[selected_simulator_key]
        input_model = sim_class.input_model
        input_data = input_model()
        result = None

    # Bygg input_html (tabell med input-felter)
    input_html = sim_class.generate_inputform(input_data)

    # Bygg rapport-html hvis resultat finnes
    report_html = sim_class.generate_report(input_data, result) if result is not None else ""

    # Bygg hele HTML med Jinja2
    input_json = input_data.model_dump()
    # Finn alle input-felter på øverste nivå
    input_fields = list(input_json.keys())
    return render_template(
        "index.html",
        selected_simulator_key=selected_simulator_key,
        simulators=SIMULATORS,
        input_html=input_html,
        report_html=report_html,
        input_json=input_json,
        input_fields=input_fields
    )

if __name__ == '__main__':
    app.run(debug=True)
