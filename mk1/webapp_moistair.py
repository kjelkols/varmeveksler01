from flask import Flask, render_template_string, request
from moistair import AirStreamInputModel, AirStream, AirStreamModel

app = Flask(__name__)

HTML = '''
<!doctype html>
<title>Moist Air Calculator</title>
<h2>Moist Air Calculator</h2>
<form method="post">
  <table>
    {% for field in fields %}
      <tr>
        <td><label for="{{ field['name'] }}">{{ field['title'] }}:</label></td>
        <td><input id="{{ field['name'] }}" name="{{ field['name'] }}" type="number" step="any" value="{{ form[field['name']] }}"></td>
      </tr>
    {% endfor %}
  </table>
  <input type="submit" value="Beregn">
</form>
{% if result %}
<h3>Resultat</h3>
<table border=1 cellpadding=4>
{% for field, value in result.dict().items() %}
  <tr><th>{{ result_titles[field] }}</th><td>{{ value }}</td></tr>
{% endfor %}
</table>
{% endif %}
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    # Hent feltinfo fra Pydantic-modellen
    fields = [
        {'name': name, 'title': field.title or name}
        for name, field in AirStreamInputModel.model_fields.items()
    ]
    form = {f['name']: 1.0 if f['name']=='mass_flow_rate' else 20.0 if f['name']=='temperature_c' else 0.5 if f['name']=='relative_humidity' else 101325 for f in fields}
    result = None
    error = None
    if request.method == 'POST':
        try:
            form = {k: float(request.form[k]) for k in form}
            input_data = AirStreamInputModel(**form)
            air_stream = AirStream.from_dict(input_data.model_dump())
            result = air_stream.to_pydantic()
        except Exception as e:
            error = str(e)
    # Resultat-titler fra AirStreamModel
    result_titles = {name: field.title or name for name, field in AirStreamModel.model_fields.items()}
    return render_template_string(HTML, form=form, result=result, fields=fields, result_titles=result_titles, error=error)

if __name__ == '__main__':
    app.run(debug=True)
