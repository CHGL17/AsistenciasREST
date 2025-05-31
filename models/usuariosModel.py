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
class ActualizarAlumnoRequest(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=50, example="Juan")
    apellidos: str | None = Field(None, min_length=2, max_length=50, example="Pérez")
    email: EmailStr | None = Field(None, example="alumno@example.com")
    password: str | None = Field(None, min_length=8, example="NuevaContraseña123")
    alumno: AlumnoModel | None = Field(
        None,
        example={
            "noControl": "20230001",
            "semestre": 5,
            "carrera": 1
        }
    )


class ActualizarTutorRequest(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=50, example="María")
    apellidos: str | None = Field(None, min_length=2, max_length=50, example="Gómez")
    email: EmailStr | None = Field(None, example="tutor@example.com")
    password: str | None = Field(None, min_length=8, example="NuevaContraseña123")
    tutor: TutorModel | None = Field(
        None,
        example={
            "noDocente": "T12345",
            "horasTutoria": 10,
            "carrera": 1,
            "nombreCarrera": "Ingeniería en Sistemas"
        }
    )


class ActualizarCoordinadorRequest(BaseModel):
    nombre: str | None = Field(None, min_length=2, max_length=50, example="Carlos")
    apellidos: str | None = Field(None, min_length=2, max_length=50, example="López")
    email: EmailStr | None = Field(None, example="coordinador@example.com")
    password: str | None = Field(None, min_length=8, example="NuevaContraseña123")
    coordinador: CoordinadorModel | None = Field(
        None,
        example={
            "noEmpleado": "CO12345",
            "departamento": "Tutorías",
            "carrera": 1,
            "nombreCarrera": "Ingeniería en Sistemas"
        }
    )

class UsuarioActualizadoResponse(BaseModel):
    id: str
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["alumno", "tutor", "coordinador"]
    fechaRegistro: datetime
    alumno: Optional[Dict] = None
    tutor: Optional[Dict] = None
    coordinador: Optional[Dict] = None

# Modelo de entrada para la eliminación de usuarios
class EliminarUsuarioRequest(BaseModel):
    no_empleado_coordinador: str = Field(
        ...,
        description="Número de empleado del coordinador que autoriza la eliminación",
        example="CO123456",
        min_length=3,
        max_length=20
    )


class UsuarioEliminadoResponse(BaseModel):
    mensaje: str
    detalles_eliminacion: dict
    coordinador_autorizador: str
    fecha_eliminacion: datetime = Field(default_factory=datetime.now)
