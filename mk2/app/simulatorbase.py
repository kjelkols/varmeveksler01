from abc import ABC, abstractmethod
from typing import Type
from pydantic import BaseModel

class SimulatorBase(ABC):
    input_model: Type[BaseModel]
    result_model: Type[BaseModel]
    name: str
    
    @staticmethod
    @abstractmethod
    def run(input_data: BaseModel) -> BaseModel:
        pass

    @staticmethod
    def generate_inputform(input_data: BaseModel) -> str:
        html = []
        for name, field in type(input_data).model_fields.items():
            value = getattr(input_data, name)
            title = field.title or name
            if field.annotation in (int, float):
                html.append(
                    f'<tr class="input-row"><th class="input-label"><label for="{name}">{title}:</label></th>'
                    f'<td><input type="number" name="{name}" id="{name}" value="{value}" step="0.1" class="input-field"></td></tr>'
                )
            else:
                html.append(
                    f'<tr class="input-row"><th class="input-label"><label for="{name}">{title}:</label></th>'
                    f'<td><input type="text" name="{name}" id="{name}" value="{value}" class="input-field"></td></tr>'
                )
        return "<table border=1 cellpadding=4 >" + "".join(html) + "</table>"

    @staticmethod
    @abstractmethod
    def generate_report(input_data: BaseModel, result_data: BaseModel) -> str:
        pass

