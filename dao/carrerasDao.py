from models.carrerasModel import CarreraInsert, CarreraUpdate, CarreraSelect, CarrerasSalida, CarreraSalida
from fastapi.encoders import jsonable_encoder
# from bson import ObjectId  # No necesitamos ObjectId para las carreras, según tu JSON

class CarreraDAO:
    def __init__(self, db):
        self.db = db

    def verificar_carrera_existente(self, carrera_id: int) -> bool:
        return self.db.carreras.find_one({"_id": carrera_id}) is not None

    async def agregar_carrera(self, carrera: CarreraInsert) -> CarreraSalida:
        salida = CarreraSalida(estatus="", mensaje="", carrera=None)
        try:
            carrera_dict = jsonable_encoder(carrera)
            carrera_dict["_id"] = carrera_dict.pop("id")
            resultado = self.db.carreras.insert_one(carrera_dict)
            if resultado.inserted_id:
                carrera_creada = self.db.carreras.find_one({"_id": resultado.inserted_id})
                carrera_select = CarreraSelect(
                    id=carrera_creada["_id"],
                    carrera=carrera_creada["carrera"],
                    nombre=carrera_creada["nombre"]
                )
                salida.estatus = "OK"
                salida.mensaje = f"Carrera creada con ID: {resultado.inserted_id}"
                salida.carrera = carrera_select
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "Error al crear la carrera"
        except Exception as ex:
            print(f"Error al crear carrera: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al agregar la carrera."
        return salida

    async def consulta_general_carreras(self) -> CarrerasSalida:
        salida = CarrerasSalida(estatus="", mensaje="", carreras=[])
        try:
            carreras_list = self.db.carreras.find()
            if not carreras_list:
                salida.estatus = "ERROR"
                salida.mensaje = "No se encontró ninguna carrera registrada."
                return salida
            carreras = []
            for carrera in carreras_list:
                carreras.append(
                    CarreraSelect(
                        id=carrera["_id"],
                        carrera=carrera["carrera"],
                        nombre=carrera["nombre"]
                    )
                )
            salida.estatus = "OK"
            salida.mensaje = "Listado de carreras."
            salida.carreras = carreras
        except Exception as ex:
            print(f"Error al consultar carreras: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar las carreras, consulte al administrador."
        return salida

    async def consultar_carrera_por_id(self, carrera_id: int) -> CarreraSalida:
        salida = CarreraSalida(estatus="", mensaje="", carrera=None)
        try:
            carrera = self.db.carreras.find_one({"_id": carrera_id})
            if not carrera:
                salida.estatus = "ERROR"
                salida.mensaje = f"Carrera con ID {carrera_id} no encontrada."
                return salida
            carrera_select = CarreraSelect(
                id=carrera["_id"],
                carrera=carrera["carrera"],
                nombre=carrera["nombre"]
            )
            salida.estatus = "OK"
            salida.mensaje = "Carrera encontrada."
            salida.carrera = carrera_select
        except Exception as ex:
            print(f"Error al consultar carrera {carrera_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar la carrera, consulte al administrador."
        return salida

    async def actualizar_carrera(self, carrera_id: int, carrera_update: CarreraUpdate) -> CarreraSalida:
        salida = CarreraSalida(estatus="", mensaje="", carrera=None)
        try:
            if not self.verificar_carrera_existente(carrera_id):
                salida.estatus = "ERROR"
                salida.mensaje = f"Carrera con ID {carrera_id} no encontrada."
                return salida

            update_data = {}
            for field, value in carrera_update.model_dump().items():
                if value is not None:
                    update_data[field] = value

            if not update_data:
                salida.estatus = "OK"
                salida.mensaje = "No se especificaron campos para actualizar."
                return salida

            resultado = self.db.carreras.update_one(
                {"_id": carrera_id},
                {"$set": update_data}
            )

            if resultado.modified_count > 0:
                carrera_actualizada = self.db.carreras.find_one({"_id": carrera_id})
                carrera_select = CarreraSelect(
                    id=carrera_actualizada["_id"],
                    carrera=carrera_actualizada["carrera"],
                    nombre=carrera_actualizada["nombre"]
                )
                salida.estatus = "OK"
                salida.mensaje = "Carrera actualizada correctamente."
                salida.carrera = carrera_select
            else:
                salida.estatus = "OK"
                salida.mensaje = "No se realizaron cambios en la carrera."
        except Exception as ex:
            print(f"Error al actualizar carrera {carrera_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar la carrera."
        return salida

    async def eliminar_carrera(self, carrera_id: int) -> CarreraSalida:
        salida = CarreraSalida(estatus="", mensaje="", carrera=None)
        try:
            if not self.verificar_carrera_existente(carrera_id):
                salida.estatus = "ERROR"
                salida.mensaje = f"Carrera con ID {carrera_id} no encontrada."
                return salida

            resultado = self.db.carreras.delete_one({"_id": carrera_id})

            if resultado.deleted_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Carrera eliminada exitosamente. ID: {carrera_id}"
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "La carrera no se pudo eliminar."
        except Exception as ex:
            print(f"Error al eliminar carrera {carrera_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al eliminar la carrera."
        return salida