from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

# Modelos para objetos anidados
class ActividadInfo(BaseModel):
    id: str
    nombre: str
    descripcion: str
    estatus: str
    obligatoria: bool

class UbicacionInfo(BaseModel):
    id: str
    nombre: str
    interno: bool
    latitud: float
    longitud: float
    estatus: str

class GrupoInfo(BaseModel):
    id: str
    nombre: str
    semestre: int
    estatus: str

class AlumnoInfo(BaseModel):
    nombre: str
    apellidos: str
    email: str
    noControl: str
    semestre: int

# Nuevo modelo para cada alumno en la lista de asistencia
class AlumnoAsistencia(BaseModel):
    id: str = Field(..., description="ID del alumno")
    fechaHoraRegistro: datetime = Field(..., description="Fecha y hora de registro")
    alumno: AlumnoInfo = Field(..., description="Información del alumno")

class AsistenciaInsert(BaseModel):
    actividad: str = Field(..., description="ObjectId de la actividad")
    fechaInicio: datetime = Field(..., description="Fecha de inicio de la asistencia")
    fechaFin: datetime = Field(..., description="Fecha de fin de la asistencia")
    horaInicio: str = Field(..., pattern=r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', description="Hora de inicio (HH:mm)")
    horaFin: str = Field(..., pattern=r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', description="Hora de fin (HH:mm)")
    estatus: Literal["Pendiente", "Realizada"] = Field(default="Pendiente", description="Estatus de la asistencia")
    ubicacion: str = Field(..., description="ObjectId de la ubicación")
    grupo: str = Field(..., description="ObjectId del grupo")
    listaAsistencia: List[str] = Field(..., description="Lista de números de control de alumnos")

# NUEVO: Modelo para actualizar asistencia (campos opcionales)
class AsistenciaUpdate(BaseModel):
    actividad: Optional[str] = Field(None, description="ObjectId de la actividad")
    fechaInicio: Optional[datetime] = Field(None, description="Fecha de inicio de la asistencia")
    fechaFin: Optional[datetime] = Field(None, description="Fecha de fin de la asistencia")
    horaInicio: Optional[str] = Field(None, pattern=r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', description="Hora de inicio (HH:mm)")
    horaFin: Optional[str] = Field(None, pattern=r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', description="Hora de fin (HH:mm)")
    estatus: Optional[Literal["Pendiente", "Realizada", "Cancelada"]] = Field(None, description="Estatus de la asistencia")
    ubicacion: Optional[str] = Field(None, description="ObjectId de la ubicación")
    grupo: Optional[str] = Field(None, description="ObjectId del grupo")
    listaAsistencia: Optional[List[str]] = Field(None, description="Lista de números de control de alumnos")

class AsistenciaSelect(BaseModel):
    id: str
    actividad: ActividadInfo
    fechaRegistro: datetime
    fechaInicio: datetime
    fechaFin: datetime
    horaInicio: str
    horaFin: str
    estatus: Literal["Pendiente", "Realizada", "Cancelada"]  # Agregado "Cancelada"
    ubicacion: UbicacionInfo
    grupo: GrupoInfo
    listaAsistencia: List[AlumnoAsistencia]

# NUEVO: Modelo específico para consulta individual (con información más detallada)
class AsistenciaDetallada(BaseModel):
    id: str
    actividad: ActividadInfo
    fechaRegistro: datetime
    fechaInicio: datetime
    fechaFin: datetime
    horaInicio: str
    horaFin: str
    estatus: Literal["Pendiente", "Realizada", "Cancelada"]
    ubicacion: UbicacionInfo
    grupo: GrupoInfo
    listaAsistencia: List[AlumnoAsistencia]
    totalAlumnos: int = Field(..., description="Total de alumnos en la lista")
    alumnosPresentes: int = Field(..., description="Número de alumnos que asistieron")
    porcentajeAsistencia: float = Field(..., description="Porcentaje de asistencia")

class Salida(BaseModel):
    estatus: str
    mensaje: str

class AsistenciaSalida(Salida):
    asistencia: Optional[AsistenciaSelect] = None

# NUEVO: Salida específica para consulta individual detallada
class AsistenciaDetalladaSalida(Salida):
    asistencia: Optional[AsistenciaDetallada] = None

class AsistenciasSalida(Salida):
    asistencias: List[AsistenciaSelect]

# NUEVO: Modelo para respuesta de eliminación
class AsistenciaEliminada(BaseModel):
    id: str
    mensaje: str
    fechaEliminacion: datetime

class AsistenciaEliminadaSalida(Salida):
    asistencia: Optional[AsistenciaEliminada] = None

# NUEVO: Modelo para filtros de búsqueda (opcional para consultas avanzadas)
class AsistenciaFiltros(BaseModel):
    actividad_id: Optional[str] = Field(None, description="Filtrar por actividad")
    grupo_id: Optional[str] = Field(None, description="Filtrar por grupo")
    estatus: Optional[Literal["Pendiente", "Realizada", "Cancelada"]] = Field(None, description="Filtrar por estatus")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha de inicio del rango")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha de fin del rango")
    ubicacion_id: Optional[str] = Field(None, description="Filtrar por ubicación")