from models.ciclosModel import CicloInsert, CicloUpdate, CicloSelect, CiclosSalida, CicloSalida, Salida
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from typing import List
from datetime import datetime

class CicloDAO:
    def __init__(self, db):
        self.db = db

    def verificar_ciclo_existente(self, ciclo_id: str) -> bool:
        return self.db.ciclos.find_one({"_id": ObjectId(ciclo_id)}) is not None

    async def agregar(self, ciclo: CicloInsert) -> CicloSalida:
        salida = Salida(estatus="", mensaje="")
        try:
            ciclo_dict = jsonable_encoder(ciclo)
            result = self.db.ciclos.insert_one(ciclo_dict)
            if result.inserted_id:
                ciclo_creado = self.db.ciclos.find_one({"_id": result.inserted_id})
                ciclo_select = CicloSelect(
                    id=str(ciclo_creado["_id"]),
                    ciclo=ciclo_creado["ciclo"],
                    fechaInicio=ciclo_creado["fechaInicio"],
                    fechaFin=ciclo_creado["fechaFin"]
                )
                salida.estatus = "OK"
                salida.mensaje = "Ciclo creado exitosamente."
                return CicloSalida(estatus=salida.estatus, mensaje=salida.mensaje, ciclo=ciclo_select)
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "Error al crear el ciclo."
                return CicloSalida(estatus=salida.estatus, mensaje=salida.mensaje)
        except Exception as ex:
            salida.estatus = "ERROR"
            salida.mensaje = f"Error al crear el ciclo: {ex}"
            return CicloSalida(estatus=salida.estatus, mensaje=salida.mensaje)

    async def consultaGeneral(self) -> CiclosSalida:
        salida = CiclosSalida(estatus="", mensaje="", ciclos=[])
        try:
            ciclos_list = self.db.ciclos.find()
            ciclos = []
            for ciclo in ciclos_list:
                ciclos.append(
                    CicloSelect(
                        id=str(ciclo["_id"]),
                        ciclo=ciclo["ciclo"],
                        fechaInicio=ciclo["fechaInicio"],
                        fechaFin=ciclo["fechaFin"]
                    )
                )
            salida.estatus = "OK"
            salida.mensaje = "Lista de ciclos obtenida correctamente."
            salida.ciclos = ciclos
        except Exception as ex:
            salida.estatus = "ERROR"
            salida.mensaje = f"Error al obtener los ciclos: {ex}"
        return salida

    async def consultarPorID(self, ciclo_id: str) -> CicloSalida:
        salida = CicloSalida(estatus="", mensaje="", ciclo=None)
        try:
            ciclo = self.db.ciclos.find_one({"_id": ObjectId(ciclo_id)})
            if ciclo:
                ciclo_select = CicloSelect(
                    id=str(ciclo["_id"]),
                    ciclo=ciclo["ciclo"],
                    fechaInicio=ciclo["fechaInicio"],
                    fechaFin=ciclo["fechaFin"]
                )
                salida.estatus = "OK"
                salida.mensaje = "Ciclo obtenido correctamente."
                salida.ciclo = ciclo_select
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "Ciclo no encontrado."
        except Exception as ex:
            salida.estatus = "ERROR"
            salida.mensaje = f"Error al obtener el ciclo: {ex}"
        return salida

    async def actualizar(self, ciclo_id: str, ciclo_update: CicloUpdate) -> CicloSalida:
        salida = CicloSalida(estatus="", mensaje="", ciclo=None)
        try:
            if not self.verificar_ciclo_existente(ciclo_id):
                salida.estatus = "ERROR"
                salida.mensaje = f"Ciclo con ID {ciclo_id} no encontrado."
                return salida

            update_data = {}
            for field, value in ciclo_update.model_dump().items():
                if value is not None:
                    if field in ["fechaInicio", "fechaFin"]:
                        value = datetime.combine(value, datetime.min.time())
                    update_data[field] = value

            if not update_data:
                salida.estatus = "OK"
                salida.mensaje = "No se especificaron campos para actualizar."
                return salida

            result = self.db.ciclos.update_one(
                {"_id": ObjectId(ciclo_id)},
                {"$set": update_data}
            )
            if result.modified_count > 0:
                ciclo_actualizado = self.db.ciclos.find_one({"_id": ObjectId(ciclo_id)})
                ciclo_select = CicloSelect(
                    id=str(ciclo_actualizado["_id"]),
                    ciclo=ciclo_actualizado["ciclo"],
                    fechaInicio=ciclo_actualizado["fechaInicio"],
                    fechaFin=ciclo_actualizado["fechaFin"]
                )
                salida.estatus = "OK"
                salida.mensaje = "Ciclo actualizado correctamente."
                salida.ciclo = ciclo_select
            else:
                salida.estatus = "OK"
                salida.mensaje = "No se realizaron cambios en el ciclo."
        except Exception as ex:
            salida.estatus = "ERROR"
            salida.mensaje = f"Error al actualizar el ciclo: {ex}"
        return salida

    async def eliminar(self, ciclo_id: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            if not self.verificar_ciclo_existente(ciclo_id):
                salida.estatus = "ERROR"
                salida.mensaje = f"Ciclo con ID {ciclo_id} no encontrado."
                return salida

            result = self.db.ciclos.delete_one({"_id": ObjectId(ciclo_id)})
            if result.deleted_count > 0:
                salida.estatus = "OK"
                salida.mensaje = "Ciclo eliminado correctamente."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo eliminar el ciclo."
        except Exception as ex:
            salida.estatus = "ERROR"
            salida.mensaje = f"Error al eliminar el ciclo: {ex}"
        return salida
