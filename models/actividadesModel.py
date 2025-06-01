from pydantic import BaseModel
from typing import List, Optional, Literal

class TutorInfo(BaseModel):
    id: str
    nombre: str

class ActividadInsert(BaseModel):
    nombre: str
    descripcion: str
    estatus: Literal["Por realizar", "Realizada", "Cancelada"]
    obligatoria: bool
    tutor_id: str | None = None  # ID del tutor para crear/actualizar

class TutorAsignacion(BaseModel):
    tutor_id: str

class ActividadSelectID(BaseModel):
    id: str
    nombre: str
    descripcion: str
    estatus: Literal["Por realizar", "Realizada", "Cancelada"]
    obligatoria: bool
    tutor: TutorInfo | None = None  # ID del tutor para crear/actualizar

class Salida(BaseModel):
    estatus: str
    mensaje: str

class ActividadesSalida(Salida):
    actividades: List[ActividadSelectID]

class ActividadesSalidaID(Salida):
    actividad: Optional[ActividadSelectID] = None