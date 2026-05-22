# Schemi Pydantic per serializzare le risposte JSON dell'API.
from pydantic import BaseModel, ConfigDict


class DatoRegionaleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    regione: str
    area: str
    anno: int
    valore: float
    interpolato: bool


class SerieAreaOut(BaseModel):
    area: str
    anno: int
    valore: float


class SerieNazionaleOut(BaseModel):
    anno: int
    valore: float
