import html
from typing import Optional, List
from pydantic import BaseModel
import enum
from string import Template

class HTMLRenderer:
    _row_template = Template('<tr><th><label for="$name">$label:</label></th><td>$input</td></tr>')
    _table_template = Template('<table border=1 cellpadding=4>$rows</table>')
    _input_number_template = Template('<input type="number" name="$name" id="$name" value="$value" step="$step">')
    _input_text_template = Template('<input type="text" name="$name" id="$name" value="$value">')
    _input_checkbox_template = Template('<input type="checkbox" name="$name" id="$name"$checked>')
    _input_select_template = Template('<select name="$name" id="$name">$options</select>')
    _option_template = Template('<option value="$value"$selected>$label</option>')

    def render_header(self, title: str, level: int) -> str:
        return f"<h{level}>{html.escape(title)}</h{level}>"

    def render_row(self, name: str, label: str, input_html: str) -> str:
        return self._row_template.substitute(name=name, label=html.escape(str(label)), input=input_html)

    def render_table(self, rows: List[str]) -> str:
        return self._table_template.substitute(rows="".join(rows))

    def render_input_number(self, name: str, value) -> str:
        try:
            step = abs(float(value)) * 0.1 if value not in (None, "", 0) else 0.1
        except Exception:
            step = 0.1
        return self._input_number_template.substitute(name=name, value=value, step=step)

    def render_input_text(self, name: str, value) -> str:
        return self._input_text_template.substitute(name=name, value=html.escape(str(value)))

    def render_input_checkbox(self, name: str, value) -> str:
        checked = " checked" if value else ""
        return self._input_checkbox_template.substitute(name=name, checked=checked)

    def render_input_enum(self, name: str, value, annotation) -> str:
        options = []
        for e in annotation:
            selected = " selected" if value == e.value else ""
            options.append(self._option_template.substitute(value=html.escape(str(e.value)), selected=selected, label=html.escape(str(e.name))))
        return self._input_select_template.substitute(name=name, options="".join(options))

    def render_model_table(self, models: List[BaseModel], headers: List[str], fields: Optional[List[str]] = None, title: Optional[str] = None) -> str:
        if not models:
            return ""
        model_type = type(models[0])
        if not all(isinstance(m, model_type) for m in models):
            raise ValueError("All models must be of the same type")
        model_fields = model_type.model_fields
        field_names = fields if fields is not None else list(model_fields.keys())
        if len(headers) != len(models):
            raise ValueError("headers must have same length as models")
        # Header row
        header_row = "<tr><th></th>" + "".join(f"<th>{html.escape(str(h))}</th>" for h in headers) + "</tr>"
        # Data rows
        data_rows = []
        for name in field_names:
            field = model_fields[name]
            label = field.title or name
            row = [f"<td>{html.escape(str(label))}</td>"]
            for model in models:
                value = getattr(model, name)
                row.append(f"<td>{html.escape(str(value))}</td>")
            data_rows.append("<tr>" + "".join(row) + "</tr>")
        return self._table_template.substitute(rows=header_row + "".join(data_rows))

class Engine:
    def __init__(self, renderer=None):
        self.parts = []
        self.renderer = renderer or HTMLRenderer()

    def write(self, text: str):
        self.parts.append(text)

    def write_header(self, title: str, level: int):
        self.parts.append(self.renderer.render_header(title, level))

    def write_input(self, model: BaseModel, title: Optional[str] = None, fields: Optional[list[str]] = None):
        if title:
            self.write_header(title, 4)
        self.parts.append('<form method="post">')
        model_fields = type(model).model_fields
        field_names = fields if fields is not None else list(model_fields.keys())
        rows = []
        for name in field_names:
            field = model_fields[name]
            label = field.title or name
            value = getattr(model, name)
            annotation = field.annotation
            if isinstance(annotation, type) and issubclass(annotation, enum.Enum):
                input_html = self.renderer.render_input_enum(name, value, annotation)
            elif annotation is bool:
                input_html = self.renderer.render_input_checkbox(name, value)
            elif annotation in (int, float):
                input_html = self.renderer.render_input_number(name, value)
            else:
                input_html = self.renderer.render_input_text(name, value)
            rows.append(self.renderer.render_row(name, label, input_html))
        self.parts.append(self.renderer.render_table(rows))
        self.parts.append('<input type="submit" value="Beregn"></form>')

    def write_model(self, model: BaseModel, fields: Optional[list[str]] = None):
        model_fields = type(model).model_fields
        field_names = fields if fields is not None else list(model_fields.keys())
        rows = []
        for name in field_names:
            field = model_fields[name]
            label = field.title or name
            value = getattr(model, name)
            rows.append(self.renderer.render_row(name, label, html.escape(str(value))))
        self.parts.append(self.renderer.render_table(rows))

    def write_model_table(self, models: list[BaseModel], headers: list[str], fields: Optional[list[str]] = None, title: Optional[str] = None):
        if title:
            self.write_header(title, 4)
        self.parts.append(self.renderer.render_model_table(models, headers, fields, title=None))

    def get_html(self) -> str:
        return "\n".join(self.parts)

# Eksempel på bruk:
if __name__ == "__main__":
    from pydantic import BaseModel, Field

    class DemoInput(BaseModel):
        mass_flow: float = Field(1.0, title="Massestrøm [kg/s]")
        temperature: float = Field(20.0, title="Temperatur [°C]")

    class DemoResult(BaseModel):
        density: float = Field(1.2, title="Tetthet [kg/m³]")
        enthalpy: float = Field(42000, title="Entalpi [J/kg]")

    input_data = DemoInput(mass_flow=1.0, temperature=20.0)
    result_data = DemoResult(density=1.2, enthalpy=42000)

    engine = Engine()
    engine.write_header("Demo av Engine-rapport", 1)
    
    engine.write("<h2>Demo-rapport</h2>Dette er en demo-rapport generert av Engine-klassen.<br> ")
    
    engine.write_header("Input data", 2)
    engine.write_input(input_data)

    engine.write_header("Result data", 2)
    engine.write_model(result_data)
    
    engine.write_header("Resultater på tabell-form", 2)
    engine.write_model_table([result_data, result_data], headers=["Kolonne 1", "Kolonne 2"])
    
    html_output = engine.get_html()
    print(html_output)
