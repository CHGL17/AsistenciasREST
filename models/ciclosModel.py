from pydantic import BaseModel
from typing import Optional
from datetime import date

class CicloInsert(BaseModel):
    ciclo: str
    fechaInicio: date
    fechaFin: date

class CicloUpdate(BaseModel):
    ciclo: Optional[str] = None
    fechaInicio: Optional[date] = None
    fechaFin: Optional[date] = None

class CicloSelect(BaseModel):
    id: str
    ciclo: str
    fechaInicio: date
    fechaFin: date

class CiclosSalida(BaseModel):
    estatus: str
    mensaje: str
    ciclos: list[CicloSelect]

class CicloSalida(BaseModel):
    estatus: str
    mensaje: str
    ciclo: Optional[CicloSelect] = None

class Salida(BaseModel):
    estatus: str
    mensaje: str