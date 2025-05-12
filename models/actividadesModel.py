from pydantic import BaseModel

class ActividadInsert(BaseModel):
    nombre: str
    descripcion: str
    estatus: str | None = "Creada"
    obligatoria: bool

class Salida(BaseModel):
    estatus: str
    mensaje: str