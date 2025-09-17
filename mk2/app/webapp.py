from flask import Flask, request
from reportgenerator.engine import Engine
from app.mysimulator import MySimulator

app = Flask(__name__)
sim = MySimulator()

@app.route('/', methods=['GET', 'POST'])
def index():
    engine = Engine()
    input_data = sim.input_model()  # default values
    result = None

    if request.method == 'POST':
        data = {k: v for k, v in request.form.items()}
        input_data = sim.input_model(**data)
        result = sim.run(input_data)

    engine.write_header("Simulator", 1)
    engine.write_input(input_data, title="Input")
    if result:
        engine.write_header("Resultat", 2)
        engine.write_model(result)
    return engine.get_html()

if __name__ == '__main__':
    app.run(debug=True)
