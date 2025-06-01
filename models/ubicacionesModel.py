from pydantic import BaseModel
from typing import List, Optional, Literal

class UbicacionInsert(BaseModel):
    nombre: str
    interno: bool = True
    latitud: float = 0.0
    longitud: float = 0.0
    estatus: Literal["Activa", "Inactiva", "Cancelada"] # Default status is 'activo'

class UbicacionUpdate(BaseModel):
    nombre: Optional[str] = None
    interno: Optional[bool] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    estatus: Optional[Literal["Activa", "Inactiva", "Cancelada"]] = None

class Salida(BaseModel):
    estatus: str
    mensaje: str

class UbicacionSelect(BaseModel):
    id: str
    nombre: str
    interno: bool
    latitud: float
    longitud: float
    estatus: Literal["Activa", "Inactiva", "Cancelada"]

class UbicacionesSalida(Salida):
    ubicaciones: List[UbicacionSelect]

class UbicacionSalida(Salida):
    ubicacion: Optional[UbicacionSelect] = None