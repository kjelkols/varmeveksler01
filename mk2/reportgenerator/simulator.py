from typing import Protocol, Type
from pydantic import BaseModel

class SimulatorProtocol(Protocol):
    input_model: Type[BaseModel]
    result_model: Type[BaseModel]

    def run(self, input_data: BaseModel) -> BaseModel:
        ...
