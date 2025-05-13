from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from datetime import datetime


class AlumnoModel(BaseModel):
    noControl: str = Field(..., min_length=8, max_length=8)
    semestre: int = Field(..., ge=1, le=12)
    carrera: int


class TutorModel(BaseModel):
    noDocente: str
    horasTutoria: int = Field(..., ge=1)
    carrera: int


class CoordinadorModel(BaseModel):
    noEmpleado: str
    departamento: str
    carrera:int


# Modelo para ALUMNO
class UsuarioAlumnoInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["alumno"]
    password: str = Field(..., min_length=8)
    alumno: AlumnoModel
    fechaRegistro: datetime = Field(default_factory=datetime.now)


# Modelo para TUTOR
class UsuarioTutorInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["tutor"]
    password: str = Field(..., min_length=8)
    tutor: TutorModel
    fechaRegistro: datetime = Field(default_factory=datetime.now)


# Modelo para COORDINADOR
class UsuarioCoordInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["coordinador"]
    password: str = Field(..., min_length=8)
    coordinador: CoordinadorModel
    fechaRegistro: datetime = Field(default_factory=datetime.now)


# Salida común
class Salida(BaseModel):
    estatus: str
    mensaje: str
