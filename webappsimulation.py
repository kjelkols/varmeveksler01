from flask import Flask, render_template_string, request
from simulationbase import MoistAirSimulation, AirflowSimulation

simulations = [MoistAirSimulation(), AirflowSimulation()]

app = Flask(__name__)

HTML = '''
<!doctype html>
<title>Generisk Simulering</title>
<style>
  body { display: flex; font-family: sans-serif; }
  .sidebar {
    width: 220px;
    background: #f4f4f4;
    padding: 20px 16px 20px 20px;
    border-right: 1px solid #ccc;
    min-height: 100vh;
    box-sizing: border-box;
  }
  .main {
    flex: 1;
    padding: 24px;
  }
  .stale-report { color: #888; }
  .stale-btn { background: #888; color: #fff; border: 1px solid #888; cursor: not-allowed; }
  .side-form { display: flex; flex-direction: column; gap: 18px; }
  .side-form label { font-weight: bold; margin-bottom: 4px; }
  .side-form select, .side-form input[type=submit] { width: 100%; }
</style>
<script>
  function markReportStale() {
    var report = document.getElementById('simreport');
    if (report) report.classList.add('stale-report');
    var btn = document.getElementById('beregnbtn');
//    if (btn) btn.classList.remove('stale-btn'); btn.disabled = false;
  }
  function clearReportStale() {
    var report = document.getElementById('simreport');
    if (report) report.classList.remove('stale-report');
    var btn = document.getElementById('beregnbtn');
//    if (btn) btn.classList.add('stale-btn'); btn.disabled = false;
  }
  window.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[type=number]').forEach(function(inp) {
      inp.addEventListener('input', markReportStale);
    });
    var form = document.getElementById('mainform');
    if (form) {
      form.addEventListener('submit', clearReportStale);
    }
    clearReportStale();
  });
</script>
<div class="sidebar">
  <form method="post" class="side-form">
    <label for="sim_select">Velg simulering:</label>
    <select name="sim_index" id="sim_select" onchange="this.form.submit()">
      {% for i in range(simulations|length) %}
        <option value="{{ i }}" {% if i == sim_index %}selected{% endif %}>{{ simulations[i].name }}</option>
      {% endfor %}
    </select>
  </form>
  <form method="post" id="mainform" class="side-form">
    <input type="hidden" name="sim_index" value="{{ sim_index }}">
    <input id="beregnbtn" type="submit" value="Beregn">
  </form>
</div>
<div class="main">
  <h2>Generisk Simulering</h2>
  <form style="margin-bottom:0;">
    <table>
      {% for field in fields %}
        <tr>
          <td><label for="{{ field['name'] }}">{{ field['title'] }}:</label></td>
          <td><input id="{{ field['name'] }}" name="{{ field['name'] }}" type="number" step="any" value="{{ form[field['name']] }}" form="mainform"></td>
        </tr>
      {% endfor %}
    </table>
  </form>
  {% if report_html %}
  <h3>Rapport</h3>
  <div id="simreport">{{ report_html|safe }}</div>
  {% endif %}
</div>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    sim_index = int(request.form.get('sim_index', 0))
    sim = simulations[sim_index]
    fields = [
        {'name': name, 'title': field.title or name}
        for name, field in sim.input_model.model_fields.items()
    ]
    # Defaultverdier
    form = {f['name']: 1.0 if f['name']=='mass_flow_rate' else 20.0 if f['name']=='temperature_c' else 0.5 if f['name']=='relative_humidity' else 101325 for f in fields}
    result = None
    report_html = None
    error = None

    # Sjekk om ALLE input-felter finnes i form-dataen (dvs. det er et beregningsskjema)
    if request.method == 'POST' and all(f['name'] in request.form for f in fields):
        try:
            form = {k: float(request.form[k]) for k in form}
            input_data = sim.input_model(**form)
            result = sim.run(input_data)
            report_html = sim.report(input_data, result, format="html")
        except Exception as e:
            error = str(e)
    # Ellers: bare vis defaultverdier for valgt simulering (ingen beregning)
    return render_template_string(HTML, form=form, result=result, fields=fields, simulations=simulations, sim_index=sim_index, report_html=report_html, error=error)

if __name__ == '__main__':
    app.run(debug=True)
