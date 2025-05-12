from models.actividadesModel import ActividadInsert, Salida
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class ActividadDAO:
    def __init__(self, db):
        self.db = db

    def agregar(self, actividad: ActividadInsert):
        salida = Salida(estatus="", mensaje="")
