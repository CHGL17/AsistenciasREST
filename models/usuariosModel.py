# Importación de librerías, modelos, etc...
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Literal, Union, Optional, Dict
from datetime import datetime


class TutorInlineModel(BaseModel):
    nombre: str
    apellidos: str
    email: str
    noDocente: str
    horasTutoria: int
    carrera: int
    nombreCarrera: str
    status: Literal["activo", "inactivo"]


class AlumnoModel(BaseModel):
    noControl: str
    semestre: int
    carrera: int
    nombreCarrera: str | None = None
    tutor: Optional[TutorInlineModel] = None


class TutorModel(BaseModel):
    noDocente: str
    horasTutoria: int
    carrera: int
    nombreCarrera: str | None = None  # Añadimos campo adicional para el nombre (Consulta ID)


class CoordinadorModel(BaseModel):
    noEmpleado: str
    departamento: str
    carrera: int
    nombreCarrera: str | None = None


# Modelo para la entrada del Alumno
class UsuarioAlumnoInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["alumno"]
    password: str
    alumno: AlumnoModel
    tutorId: Optional[str] = Field(default=None, description="ID del tutor asignado")
    status: Literal["activo", "inactivo"] = "activo"
    fechaRegistro: datetime = Field(default_factory=datetime.now)


# Modelo para la entrada del Tutor
class UsuarioTutorInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["tutor"]
    password: str
    tutor: TutorModel
    status: Literal["activo", "inactivo"] = "activo"
    fechaRegistro: datetime = Field(default_factory=datetime.now)


# Modelo para la entrada del Coordinador
class UsuarioCoordInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["coordinador"]
    password: str
    coordinador: CoordinadorModel
    status: Literal["activo", "inactivo"] = "activo"
    fechaRegistro: datetime = Field(default_factory=datetime.now)


# Retorna los datos validados en la salida
class Salida(BaseModel):
    estatus: str
    mensaje: str


# Modelo de entrada para la consulta Individual de usuarios
class UsuarioBaseResponse(BaseModel):
    id: str
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: str
    fechaRegistro: datetime
    status: str  # activo o inactivo


class AlumnoResponse(UsuarioBaseResponse):
    alumno: AlumnoModel


class TutorResponse(UsuarioBaseResponse):
    tutor: TutorModel


class CoordinadorResponse(UsuarioBaseResponse):
    coordinador: CoordinadorModel


class UsuarioSalidaID(Salida):
    usuario: Union[AlumnoResponse, TutorResponse, CoordinadorResponse, None] = None


# Modelo de entrada para la consulta General de usuarios

class UsuarioSalidaLista(Salida):
    usuarios: list[Union[AlumnoResponse, TutorResponse, CoordinadorResponse]] = []


# Modelo de entrada para la Modificación del usuario
# class ActualizarAlumnoRequest(BaseModel):
#     email: EmailStr = Field(..., example="alumno@example.com")
#     nombre: str = Field(..., example="Luis")
#     apellidos: str = Field(..., example="García")
#     tipo: Literal["alumno"]
#     password: str = Field(..., min_length=8, example="Hola.123!")
#     alumno: AlumnoModel
#     tutorId: Optional[str] = Field(default=None, example="663b21ddfa41c12fcf17415e")
#     status: Literal["activo", "inactivo"] = Field(..., example="activo")
#     tutorId: Optional[str] = Field(default=None, example="663b21ddfa41c12fcf17415e")
#
#
#
# class ActualizarTutorRequest(BaseModel):
#     email: EmailStr = Field(..., example="tutor@example.com")
#     nombre: str = Field(..., example="María")
#     apellidos: str = Field(..., example="Gómez")
#     tipo: Literal["tutor"]
#     password: str = Field(..., min_length=8, example="Hola.123!")
#     tutor: TutorModel
#     status: Literal["activo", "inactivo"] = Field(..., example="activo")
#     fechaRegistro: datetime = Field(default_factory=datetime.now)
#
#
# class ActualizarCoordinadorRequest(BaseModel):
#     email: EmailStr = Field(..., example="coordinador@example.com")
#     nombre: str = Field(..., example="Carlos")
#     apellidos: str = Field(..., example="Lopez")
#     tipo: Literal["coordinador"]
#     password: str = Field(..., min_length=8, example="Hola.123!")
#     coordinador: CoordinadorModel
#     status: Literal["activo", "inactivo"] = Field(..., example="activo")
#     fechaRegistro: datetime = Field(default_factory=datetime.now)


# class UsuarioActualizadoResponse(BaseModel):
#     id: str
#     email: EmailStr
#     nombre: str
#     apellidos: str
#     tipo: Literal["alumno", "tutor", "coordinador"]
#     fechaRegistro: datetime
#     alumno: Optional[Dict] = None
#     tutor: Optional[Dict] = None
#     coordinador: Optional[Dict] = None


# Modelo de salida para la eliminación de usuarios
class UsuarioEliminadoResponse(BaseModel):
    mensaje: str
    detalles_eliminacion: dict
    fecha_eliminacion: datetime = Field(default_factory=datetime.now)
