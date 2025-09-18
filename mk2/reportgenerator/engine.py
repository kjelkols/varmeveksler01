import html
import enum
from typing import Optional, List
from pydantic import BaseModel
try:
    from .htmlrenderer import HTMLRenderer
except ImportError:
    from htmlrenderer import HTMLRenderer

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

    def write_model(self, model: BaseModel, fields: Optional[list[str]] = None, table_style: Optional[str] = None):
        model_fields = type(model).model_fields
        field_names = fields if fields is not None else list(model_fields.keys())
        rows = []
        for name in field_names:
            field = model_fields[name]
            label = field.title or name
            value = getattr(model, name)
            rows.append(self.renderer.render_row(name, label, html.escape(str(value))))
        self.parts.append(self.renderer.render_table(rows, table_style=table_style))

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
