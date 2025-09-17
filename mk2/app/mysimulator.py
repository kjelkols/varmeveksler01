from pydantic import BaseModel, Field
from reportgenerator.simulator import SimulatorProtocol

class MyInput(BaseModel):
    x: float = Field(0.0, title="X-verdi")
    y: float = Field(0.0, title="Y-verdi")

class MyResult(BaseModel):
    sum: float = Field(..., title="Sum")


class MySimulator:
    input_model = MyInput
    result_model = MyResult

    def run(self, input_data: MyInput) -> MyResult:
        return MyResult(sum=input_data.x + input_data.y)
