from pydantic import BaseModel
from typing import List, Optional

class CarreraInsert(BaseModel):
    id: int
    carrera: str
    nombre: str

class CarreraUpdate(BaseModel):
    carrera: Optional[str] = None
    nombre: Optional[str] = None

class CarreraSelect(BaseModel):
    id: int  # Usamos int en lugar de str, según tu JSON de ejemplo
    carrera: str
    nombre: str

class CarrerasSalida(BaseModel):  # No hereda de Salida, estructura diferente
    estatus: str
    mensaje: str
    carreras: List[CarreraSelect]

class CarreraSalida(BaseModel):  # No hereda de Salida, estructura diferente
    estatus: str
    mensaje: str
    carrera: Optional[CarreraSelect] = None