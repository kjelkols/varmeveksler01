
import html
from typing import Optional, List
from pydantic import BaseModel
from string import Template
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os


class HTMLRenderer:
    _row_template = Template('<tr class="input-row $row_class"><th class="input-label $label_class"><label for="$name">$label:</label></th><td>$input</td></tr>')
    _table_template = Template('<table class="input-table" border=1 cellpadding=4 $style>$rows</table>')
    _input_number_template = Template('<input type="number" name="$name" id="$name" value="$value" step="$step" class="input-field $extra_class">')
    _input_text_template = Template('<input type="text" name="$name" id="$name" value="$value" class="input-field $extra_class">')
    _input_checkbox_template = Template('<input type="checkbox" name="$name" id="$name" class="input-field"$checked>')
    _input_select_template = Template('<select name="$name" id="$name" class="input-field">$options</select>')
    _option_template = Template('<option value="$value"$selected>$label</option>')

    def __init__(self):
        # Set up Jinja2 environment for templates
        template_dir = os.path.join(os.path.dirname(__file__), "templates")
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def render_header(self, title: str, level: int) -> str:
        return f"<h{level}>{html.escape(title)}</h{level}>"

    def render_row(self, name: str, label: str, input_html: str, row_class: str = "", label_class: str = "") -> str:
        return self._row_template.substitute(name=name, label=html.escape(str(label)), input=input_html, row_class=row_class, label_class=label_class)

    def render_table(self, rows: List[str], table_style: Optional[str] = None, row_class: str = "", label_class: str = "") -> str:
        style = f'style="{table_style}"' if table_style else ''
        # rows is a list of html strings, but we want to inject row_class/label_class into each row
        # så vi antar at render_row kalles med riktige klassenavn
        return self._table_template.substitute(rows="".join(rows), style=style)

    def render_input_number(self, name: str, value, extra_class: str = "") -> str:
        try:
            step = abs(float(value)) * 0.1 if value not in (None, "", 0) else 0.1
        except Exception:
            step = 0.1
        return self._input_number_template.substitute(name=name, value=value, step=step, extra_class=extra_class)

    def render_input_text(self, name: str, value, extra_class: str = "") -> str:
        return self._input_text_template.substitute(name=name, value=html.escape(str(value)), extra_class=extra_class)

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

        # Prepare data for Jinja2
        rows = []
        for name in field_names:
            field = model_fields[name]
            label = field.title or name
            vals = [html.escape(str(getattr(model, name))) for model in models]
            rows.append({"label": label, "vals": vals})

        template = self.jinja_env.get_template("model_table.html")
        return template.render(headers=headers, rows=rows)
