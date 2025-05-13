from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

class AlumnoModel(BaseModel):
    noControl: str = Field(..., min_length=8, max_length=8)
    semestre: int = Field(..., ge=1, le=12)
    carrera: int

class TutorModel(BaseModel):
    noDocente: str
    horasTutoria: int = Field(..., ge=1)
    carrera: str  # ObjectId como string

class CoordinadorModel(BaseModel):
    noEmpleado: str
    departamento: str

class UsuarioInsert(BaseModel):
    email: EmailStr
    nombre: str
    apellidos: str
    tipo: Literal["alumno", "tutor", "coordinador"]
    password: str = Field(..., min_length=8)
    alumno: Optional[AlumnoModel] = None
    tutor: Optional[TutorModel] = None
    coordinador: Optional[CoordinadorModel] = None
    fechaRegistro: datetime = Field(default_factory=datetime.now)

class Salida(BaseModel):
    estatus: str
    mensaje: str
