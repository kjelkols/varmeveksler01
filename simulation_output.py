from pydantic import BaseModel
from models import AirStreamInput, ExchangerInput
from models import HeatExchangerParameters, HeatExchangerResults

class SimulationOutput(BaseModel):
    airstream_1: AirStreamInput
    airstream_2: AirStreamInput
    exchanger: ExchangerInput
    parameters: HeatExchangerParameters
    results: HeatExchangerResults
