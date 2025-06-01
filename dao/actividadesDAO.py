from models.actividadesModel import ActividadInsert, Salida, ActividadesSalida, ActividadSelectID, ActividadesSalidaID
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class ActividadDAO:
    def __init__(self, db):
        self.db = db

    def agregar(self, actividad: ActividadInsert):
        salida = Salida(estatus="", mensaje="")
        try:
            # Verificar si ya existe una actividad con el mismo nombre
            actividad_existente = self.db.actividades.find_one({"nombre": actividad.nombre})
            if actividad_existente:
                salida.estatus = "ERROR"
                salida.mensaje = "Ya existe una actividad con este nombre."
                return salida

            nueva_actividad = jsonable_encoder(actividad)
            resultado = self.db.actividades.insert_one(nueva_actividad)
            if resultado.inserted_id:
                actividad_creada = self.db.actividades.find_one(
                    {"_id": resultado.inserted_id}
                )
                actividad_select = ActividadSelectID(
                    id=str(actividad_creada["_id"]),
                    nombre=actividad_creada["nombre"],
                    descripcion=actividad_creada["descripcion"],
                    estatus=actividad_creada["estatus"],
                    obligatoria=actividad_creada["obligatoria"]
                )
                return {
                    "estatus": "OK",
                    "mensaje": "Actividad creada exitosamente",
                    "actividad": actividad_select
                }
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "Error al crear la actividad"
                return salida
        except Exception as e:
            salida.mensaje = f"Error al crear la actividad: {str(e)}"
            salida.estatus = "ERROR"
            return salida

    def consultaGeneral(self) -> ActividadesSalida:
        salida = ActividadesSalida(estatus="", mensaje="", actividades=[])
        try:
            actividades_list = self.db.actividades.find()
            if not actividades_list:
                salida.estatus = "ERROR"
                salida.mensaje = "No se encontró ninguna actividad registrada."
                return salida
            actividades = []
            for actividad in actividades_list:
                actividades.append(
                    ActividadSelectID(
                        id=str(actividad["_id"]),
                        nombre=actividad["nombre"],
                        descripcion=actividad["descripcion"],
                        estatus=actividad["estatus"],
                        obligatoria=actividad["obligatoria"]
                    )
                )
            salida.estatus = "OK"
            salida.mensaje = "Listado de actividades."
            salida.actividades = actividades
        except Exception as ex:
            print(f"Error al consultar actividades: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar las actividades, consulte al administrador."
        return salida

    def consultarActividadPorID(self, actividad_id: str) -> ActividadesSalidaID:
        salida = ActividadesSalidaID(estatus="", mensaje="", actividad=None)
        try:
            actividad = self.db.actividades.find_one({"_id": ObjectId(actividad_id)})
            if not actividad:
                salida.estatus = "ERROR"
                salida.mensaje = f"Actividad con ID {actividad_id} no encontrada."
                return salida
            actividad_select = ActividadSelectID(
                id=str(actividad["_id"]),
                nombre=actividad["nombre"],
                descripcion=actividad["descripcion"],
                estatus=actividad["estatus"],
                obligatoria=actividad["obligatoria"]
            )
            salida.estatus = "OK"
            salida.mensaje = "Actividad encontrada."
            salida.actividad = actividad_select
        except Exception as ex:
            print(f"Error al consultar actividad {actividad_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar la actividad, consulte al administrador."
        return salida

    def actualizar(self, actividad_id: str, actividad_update: ActividadInsert) -> ActividadesSalidaID:
        salida = ActividadesSalidaID(estatus="", mensaje="", actividad=None)
        try:
            _id_obj = ObjectId(actividad_id) if ObjectId.is_valid(actividad_id) else actividad_id
            actividad_existente_mismo_nombre = self.db.actividades.find_one({
                "nombre": actividad_update.nombre,
                "_id": {"$ne": _id_obj}
            })
            if actividad_existente_mismo_nombre:
                salida.estatus = "ERROR"
                salida.mensaje = f"Ya existe otra actividad con el nombre '{actividad_update.nombre}'."
                return salida

            actividad_existente = self.db.actividades.find_one({"_id": _id_obj})
            if not actividad_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"Actividad con ID {actividad_id} no encontrada."
                return salida

            actividad_dict = actividad_update.dict()
            update_data = {
                "nombre": actividad_dict["nombre"],
                "descripcion": actividad_dict["descripcion"],
                "estatus": actividad_dict["estatus"],
                "obligatoria": actividad_dict["obligatoria"]
            }

            resultado = self.db.actividades.update_one(
                {"_id": _id_obj},
                {"$set": update_data}
            )
            if resultado.modified_count > 0:
                actividad_actualizada = self.db.actividades.find_one({"_id": _id_obj})
                actividad_select = ActividadSelectID(
                    id=str(actividad_actualizada["_id"]),
                    nombre=actividad_actualizada["nombre"],
                    descripcion=actividad_actualizada["descripcion"],
                    estatus=actividad_actualizada["estatus"],
                    obligatoria=actividad_actualizada["obligatoria"]
                )
                salida.estatus = "OK"
                salida.mensaje = "Actividad actualizada correctamente."
                salida.actividad = actividad_select
            else:
                # Si no se modificó nada, podría ser porque los datos son los mismos
                # o porque la actividad no se encontró (aunque ya se verificó antes).
                # Consideramos que si no hay error y no se modificó, es porque los datos eran iguales.
                salida.estatus = "OK"
                salida.mensaje = "No se realizaron cambios en la actividad (posiblemente los datos ya eran los mismos)."
                actividad_actual = self.db.actividades.find_one({"_id": _id_obj})
                if actividad_actual:
                    salida.actividad = ActividadSelectID(
                        id=str(actividad_actual["_id"]),
                        nombre=actividad_actual["nombre"],
                        descripcion=actividad_actual["descripcion"],
                        estatus=actividad_actual["estatus"],
                        obligatoria=actividad_actual["obligatoria"]
                    )
        except Exception as ex:
            print(f"Error al actualizar actividad {actividad_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar la actividad."
        return salida

    def cancelar(self, actividad_id: str) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            _id_obj = ObjectId(actividad_id) if ObjectId.is_valid(actividad_id) else actividad_id
            actividad_existente = self.db.actividades.find_one({"_id": _id_obj})

            if not actividad_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"Actividad con ID {actividad_id} no encontrada."
                return salida

            if actividad_existente.get("estatus") == "Cancelada":
                salida.estatus = "OK"
                salida.mensaje = f"La actividad con ID {actividad_id} ya se encuentra cancelada."
                return salida

            resultado = self.db.actividades.update_one(
                {"_id": _id_obj},
                {"$set": {"estatus": "Cancelada"}}
            )

            if resultado.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Actividad con ID {actividad_id} cancelada exitosamente."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "La actividad no se pudo cancelar. Verifique el estado actual."
        except Exception as ex:
            print(f"Error al cancelar actividad {actividad_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al cancelar la actividad."
        return salida