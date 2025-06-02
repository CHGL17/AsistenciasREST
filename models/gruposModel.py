from pydantic import BaseModel
from typing import List, Optional, Literal

from .ciclosModel import CicloSelect
from .carrerasModel import CarreraSelect

class TutorView(BaseModel):
    id: str
    nombre: str
    apellidos: str
    email: str
    noDocente: str
    horasTutoria: int
    status: str

class AlumnoView(BaseModel):
    id: str
    nombre: str
    apellidos: str
    email: str
    noControl: str
    semestre: int
    status: str

class GrupoInsert(BaseModel):
    nombre: str
    semestre: int
    ciclo: str  # ObjectId as string reference to ciclos collection
    carrera: int  # ObjectId as string reference to carreras collection
    tutor: str  # ObjectId as string reference to usuarios collection
    alumnos: List[str]  # List of ObjectId as string references to usuarios collection
    estatus: Literal["activo", "inactivo"] = "activo"  # Campo de estatus añadido

class GrupoUpdate(BaseModel):
    nombre: Optional[str] = None
    semestre: Optional[int] = None
    ciclo: Optional[str] = None  # ObjectId as string reference to ciclos collection
    carrera: Optional[int] = None  # ObjectId as string reference to carreras collection
    tutor: Optional[str] = None  # ObjectId as string reference to usuarios collection
    alumnos: Optional[List[str]] = None  # List of ObjectId as string references to usuarios collection
    estatus: Optional[Literal["activo", "inactivo"]] = None  # Campo de estatus añadido

class Salida(BaseModel):
    estatus: str
    mensaje: str

class GrupoSelect(BaseModel):
    id: str
    nombre: str
    semestre: int
    ciclo: CicloSelect
    carrera: CarreraSelect
    tutor: TutorView
    alumnos: List[AlumnoView]
    estatus: Literal["activo", "inactivo"]  # Campo de estatus añadido

class GruposSalida(Salida):
    grupos: List[GrupoSelect]
    
class GrupoSalida(Salida):
    grupo: Optional[GrupoSelect] = None