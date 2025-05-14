from pydantic import BaseModel
from typing import List, Optional
# from datetime import datetime
        
class GrupoInsert(BaseModel):
    nombre: str
    semestre: int
    ciclo: str  # ObjectId as string reference to ciclos collection
    carrera: int  # ObjectId as string reference to carreras collection
    tutor: str  # ObjectId as string reference to usuarios collection
    alumnos: List[str]  # List of ObjectId as string references to usuarios collection

class GrupoUpdate(BaseModel):
    nombre: Optional[str] = None
    semestre: Optional[int] = None
    ciclo: Optional[str] = None  # ObjectId as string reference to ciclos collection
    carrera: Optional[int] = None  # ObjectId as string reference to carreras collection
    tutor: Optional[str] = None  # ObjectId as string reference to usuarios collection
    alumnos: Optional[List[str]] = None  # List of ObjectId as string references to usuarios collection

class Salida(BaseModel):
    estatus: str
    mensaje: str

class GrupoSelect(BaseModel):
    id: str
    nombre: str
    semestre: int
    ciclo: str
    carrera: int
    tutor: str
    alumnos: List[str]

class GruposSalida(Salida):
    grupos: List[GrupoSelect]
    
class GrupoSalida(Salida):
    grupo: Optional[GrupoSelect] = None