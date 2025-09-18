
from typing import Type
from pydantic import BaseModel, Field
from .simulatorbase import SimulatorBase
from reportgenerator.engine import Engine

# Example simulator implementations. To simple examples of how to create simulators, two simple simulators are defined here.
# MySimulator1 adds two numbers, MySimulator2 multiplies two numbers.
# Engine is used to generate reports in HTML format with proper css-classes.

class MyInput1(BaseModel):
    x: float = Field(1.0, title="X-verdi")
    y: float = Field(2.0, title="Y-verdi")

class MyResult1(BaseModel):
    sum: float = Field(..., title="Sum")

class MySimulator1(SimulatorBase):
    label = "Addisjon"
    input_model = MyInput1
    result_model = MyResult1

    @staticmethod
    def run(input_data: BaseModel) -> BaseModel:
        data = input_data if isinstance(input_data, MyInput1) else MyInput1(**input_data.model_dump())
        return MyResult1(sum=data.x + data.y)

    @staticmethod
    def generate_report(input_data: BaseModel, result_data: BaseModel) -> str:
#        data = input_data if isinstance(input_data, MyInput1) else MyInput1(**input_data.model_dump())
#        result = result_data if isinstance(result_data, MyResult1) else MyResult1(**result_data.model_dump())
        eng = Engine()
        eng.write_header("Addisjon", level=2)
        eng.write_model(input_data)
        eng.write_model(result_data)
        return eng.get_html()

class MyInput2(BaseModel):
    a: float = Field(3.0, title="Første verdi")
    b: float = Field(4.0, title="Andre verdi")

class MyResult2(BaseModel):
    produkt: float = Field(..., title="Produkt")

class MySimulator2(SimulatorBase):
    label = "Multiplikasjon"
    input_model = MyInput2
    result_model = MyResult2


    @staticmethod
    def run(input_data: BaseModel) -> BaseModel:
        data = input_data if isinstance(input_data, MyInput2) else MyInput2(**input_data.model_dump())
        return MyResult2(produkt=data.a * data.b)

    @staticmethod
    def generate_report(input_data: BaseModel, result_data: BaseModel) -> str:
        data = input_data if isinstance(input_data, MyInput2) else MyInput2(**input_data.model_dump())
        result = result_data if isinstance(result_data, MyResult2) else MyResult2(**result_data.model_dump())
        html = ["<h2>Resultat for Multiplikasjon. Denne teksten er skrevet manuelt som direkte html.</h2>"]
        html.append(f"<p>Første verdi: <b>{data.a}</b></p>")
        html.append(f"<p>Andre verdi: <b>{data.b}</b></p>")
        html.append(f"<p>Produkt: <span class='result-block'><b>{result.produkt}</b></span></p>")
        return '\n'.join(html)
