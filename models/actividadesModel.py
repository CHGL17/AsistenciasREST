from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

class ActividadInsert(BaseModel):
    nombre: str
    descripcion: str
    estatus: Literal["Por realizar", "Realizada", "Cancelada"]
    obligatoria: bool | None = False
    ubicacion: str  # ID de la ubicación
    fechaCreacion: datetime | datetime = datetime.now()

class Salida(BaseModel):
    estatus: str
    mensaje: str

class ActividadSelect(BaseModel):
    nombre: str
    descripcion: str
    estatus: str
    obligatoria: bool
    ubicacion: str  # ID de la ubicación
    fechaCreacion: datetime

class ActividadesSalida(Salida):
    actividades: list[ActividadSelect]

class ActividadSelectID(BaseModel):
    _id: str
    nombre: str
    descripcion: str
    estatus: str
    obligatoria: bool
    ubicacion: str
    fechaCreacion: datetime

class ActividadesSalidaID(Salida):
    actividad: ActividadSelectID | None = None