# Importación de librerías, modelos, etc...
from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Union
from datetime import datetime


class AlumnoModel(BaseModel):
    noControl: str
    semestre: int
    carrera: int


class TutorModel(BaseModel):
    noDocente: str
    horasTutoria: int
    carrera: int
    nombreCarrera: str | None = None  # Añadimos campo adicional para el nombre (Consulta ID)


class CoordinadorModel(BaseModel):
    noEmpleado: str
    departamento: str
    carrera: int


# Modelo para la entrada del Alumno
class UsuarioAlumnoInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["alumno"]
    password: str
    alumno: AlumnoModel
    fechaRegistro: datetime = Field(default_factory=datetime.now)


# Modelo para la entrada del Tutor
class UsuarioTutorInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["tutor"]
    password: str
    tutor: TutorModel
    fechaRegistro: datetime = Field(default_factory=datetime.now)


# Modelo para la entrada del Coordinador
class UsuarioCoordInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["coordinador"]
    password: str
    coordinador: CoordinadorModel
    fechaRegistro: datetime = Field(default_factory=datetime.now)


# Retorna los datos validados en la salida
class Salida(BaseModel):
    estatus: str
    mensaje: str
    id_usuario: str | None = None


# Modelo de entrada para la consulta Individual de usuarios
class UsuarioBaseResponse(BaseModel):
    id: str
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: str
    fechaRegistro: datetime


class AlumnoResponse(UsuarioBaseResponse):
    alumno: AlumnoModel
    nombreCarrera: str | None = None  # Añadimos campo adicional para el nombre

class TutorResponse(UsuarioBaseResponse):
    tutor: TutorModel
    nombreCarrera: str | None = None

class CoordinadorResponse(UsuarioBaseResponse):
    coordinador: CoordinadorModel
    nombreCarrera: str | None = None

class UsuarioSalidaID(Salida):
    usuario: Union[AlumnoResponse, TutorResponse, CoordinadorResponse, None] = None

