from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class ActividadInsert(BaseModel):
    nombre: str
    descripcion: str
    estatus: Literal["Por realizar", "Cancelada", "Realizada"]
    obligatoria: bool | None = False

class Salida(BaseModel):
    estatus: str
    mensaje: str

class ActividadSelect(BaseModel):
    nombre: str
    descripcion: str
    estatus: str
    obligatoria: bool

class ActividadesSalida(Salida):
    actividades: list[ActividadSelect]

class ActividadSelectID(BaseModel):
    _id: str
    nombre: str
    descripcion: str
    estatus: str
    obligatoria: bool

class ActividadesSalidaID(Salida):
    actividad: ActividadSelectID | None = None