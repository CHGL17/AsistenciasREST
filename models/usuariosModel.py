#Importación de librerías, modelos, etc...
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from datetime import datetime


class AlumnoModel(BaseModel):
    noControl: str
    semestre: int
    carrera: int


class TutorModel(BaseModel):
    noDocente: str
    horasTutoria: int
    carrera: int


class CoordinadorModel(BaseModel):
    noEmpleado: str
    departamento: str
    carrera: int

#Modelo para la entrada del Alumno
class UsuarioAlumnoInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["alumno"]
    password: str
    alumno: AlumnoModel
    fechaRegistro: datetime = Field(default_factory=datetime.now)

#Modelo para la entrada del Tutor
class UsuarioTutorInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["tutor"]
    password: str
    tutor: TutorModel
    fechaRegistro: datetime = Field(default_factory=datetime.now)

#Modelo para la entrada del Coordinador
class UsuarioCoordInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["coordinador"]
    password: str
    coordinador: CoordinadorModel
    fechaRegistro: datetime = Field(default_factory=datetime.now)

#Retorna los datos validados en la salida
class Salida(BaseModel):
    estatus: str
    mensaje: str
    id_usuario: str | None = None
