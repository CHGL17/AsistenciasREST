from models.ubicacionesModel import UbicacionInsert, Salida, UbicacionSalida, UbicacionSelect, UbicacionesSalida
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class UbicacionesDAO:
    def __init__(self, db):
        self.db = db

    def crear_ubicacion(self, ubicacion: UbicacionInsert):
        """
        Crea una nueva ubicación verificando que el nombre no esté duplicado
        """
        try:
            # Verificar si ya existe una ubicación con el mismo nombre
            ubicacion_existente = self.db.ubicaciones.find_one({
                "nombre": ubicacion.nombre,
                "estatus": {"$ne": "Cancelada"}
            })
            
            if ubicacion_existente:
                return {
                    "estatus": "ERROR",
                    "mensaje": f"Ya existe una ubicación con el nombre '{ubicacion.nombre}'",
                    "ubicacion": None
                }

            nueva_ubicacion = jsonable_encoder(ubicacion)
            resultado = self.db.ubicaciones.insert_one(nueva_ubicacion)
            
            if resultado.inserted_id:
                ubicacion_creada = self.db.ubicaciones.find_one(
                    {"_id": resultado.inserted_id}
                )
                ubicacion_select = UbicacionSelect(
                    id=str(ubicacion_creada["_id"]),
                    nombre=ubicacion_creada["nombre"],
                    interno=ubicacion_creada["interno"],
                    latitud=ubicacion_creada["latitud"],
                    longitud=ubicacion_creada["longitud"],
                    estatus=ubicacion_creada["estatus"]
                )
                return {
                    "estatus": "OK",
                    "mensaje": "Ubicación creada exitosamente",
                    "ubicacion": ubicacion_select
                }
            else:
                return {
                    "estatus": "ERROR",
                    "mensaje": "Error al crear la ubicación",
                    "ubicacion": None
                }
                
        except Exception as e:
            return {
                "estatus": "ERROR",
                "mensaje": f"Error al crear la ubicación: {str(e)}",
                "ubicacion": None
            }

    def obtener_ubicaciones(self) -> UbicacionesSalida:
        """
        Obtiene todas las ubicaciones activas
        """
        salida = UbicacionesSalida(estatus="", mensaje="", ubicaciones=[])
        try:
            ubicaciones_list = self.db.ubicaciones.find({
                "estatus": {"$ne": "Cancelada"}
            }).sort("nombre", 1)
            
            ubicaciones = []
            for ubicacion in ubicaciones_list:
                ubicaciones.append(
                    UbicacionSelect(
                        id=str(ubicacion["_id"]),
                        nombre=ubicacion["nombre"],
                        interno=ubicacion["interno"],
                        latitud=ubicacion["latitud"],
                        longitud=ubicacion["longitud"],
                        estatus=ubicacion["estatus"]
                    )
                )
            
            salida.estatus = "OK"
            salida.mensaje = "Listado de ubicaciones obtenido exitosamente"
            salida.ubicaciones = ubicaciones
            
        except Exception as ex:
            print(f"Error al consultar ubicaciones: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar las ubicaciones, consulte al administrador"
            
        return salida

    def obtener_ubicacion_por_id(self, ubicacion_id: str) -> UbicacionSalida:
        """
        Obtiene una ubicación específica por su ID
        """
        salida = UbicacionSalida(estatus="", mensaje="", ubicacion=None)
        try:
            _id_obj = ObjectId(ubicacion_id) if ObjectId.is_valid(ubicacion_id) else ubicacion_id
            ubicacion = self.db.ubicaciones.find_one({
                "_id": _id_obj,
                "estatus": {"$ne": "Cancelada"}
            })
            
            if not ubicacion:
                salida.estatus = "ERROR"
                salida.mensaje = f"Ubicación con ID {ubicacion_id} no encontrada"
                return salida
                
            ubicacion_select = UbicacionSelect(
                id=str(ubicacion["_id"]),
                nombre=ubicacion["nombre"],
                interno=ubicacion["interno"],
                latitud=ubicacion["latitud"],
                longitud=ubicacion["longitud"],
                estatus=ubicacion["estatus"]
            )
            
            salida.estatus = "OK"
            salida.mensaje = "Ubicación encontrada exitosamente"
            salida.ubicacion = ubicacion_select
            
        except Exception as ex:
            print(f"Error al consultar ubicación {ubicacion_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar la ubicación, consulte al administrador"
            
        return salida

    def editar_ubicacion(self, ubicacion_id: str, ubicacion_update: UbicacionInsert) -> UbicacionSalida:
        """
        Edita una ubicación verificando que el nombre no esté duplicado
        """
        salida = UbicacionSalida(estatus="", mensaje="", ubicacion=None)
        try:
            _id_obj = ObjectId(ubicacion_id) if ObjectId.is_valid(ubicacion_id) else ubicacion_id
            
            # Verificar si existe otra ubicación con el mismo nombre
            ubicacion_existente_mismo_nombre = self.db.ubicaciones.find_one({
                "nombre": ubicacion_update.nombre,
                "_id": {"$ne": _id_obj},
                "estatus": {"$ne": "Cancelada"}
            })
            
            if ubicacion_existente_mismo_nombre:
                salida.estatus = "ERROR"
                salida.mensaje = f"Ya existe otra ubicación con el nombre '{ubicacion_update.nombre}'"
                return salida

            # Verificar si la ubicación a actualizar existe
            ubicacion_existente = self.db.ubicaciones.find_one({
                "_id": _id_obj,
                "estatus": {"$ne": "Cancelada"}
            })
            
            if not ubicacion_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"Ubicación con ID {ubicacion_id} no encontrada"
                return salida

            ubicacion_dict = ubicacion_update.model_dump()
            update_data = {
                "nombre": ubicacion_dict["nombre"],
                "interno": ubicacion_dict["interno"],
                "latitud": ubicacion_dict["latitud"],
                "longitud": ubicacion_dict["longitud"],
                "estatus": ubicacion_dict["estatus"]
            }

            resultado = self.db.ubicaciones.update_one(
                {"_id": _id_obj},
                {"$set": update_data}
            )
            
            if resultado.modified_count > 0:
                ubicacion_actualizada = self.db.ubicaciones.find_one({"_id": _id_obj})
                ubicacion_select = UbicacionSelect(
                    id=str(ubicacion_actualizada["_id"]),
                    nombre=ubicacion_actualizada["nombre"],
                    interno=ubicacion_actualizada["interno"],
                    latitud=ubicacion_actualizada["latitud"],
                    longitud=ubicacion_actualizada["longitud"],
                    estatus=ubicacion_actualizada["estatus"]
                )
                salida.estatus = "OK"
                salida.mensaje = "Ubicación actualizada correctamente"
                salida.ubicacion = ubicacion_select
            else:
                # Si no se modificó nada, devolver la ubicación actual
                salida.estatus = "OK"
                salida.mensaje = "No se realizaron cambios en la ubicación (posiblemente los datos ya eran los mismos)"
                ubicacion_actual = self.db.ubicaciones.find_one({"_id": _id_obj})
                if ubicacion_actual:
                    salida.ubicacion = UbicacionSelect(
                        id=str(ubicacion_actual["_id"]),
                        nombre=ubicacion_actual["nombre"],
                        interno=ubicacion_actual["interno"],
                        latitud=ubicacion_actual["latitud"],
                        longitud=ubicacion_actual["longitud"],
                        estatus=ubicacion_actual["estatus"]
                    )
                    
        except Exception as ex:
            print(f"Error al actualizar ubicación {ubicacion_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar la ubicación"
            
        return salida

    def cancelar_ubicacion(self, ubicacion_id: str) -> Salida:
        """
        Cancela una ubicación (cambio lógico de estatus)
        """
        salida = Salida(estatus="", mensaje="")
        try:
            _id_obj = ObjectId(ubicacion_id) if ObjectId.is_valid(ubicacion_id) else ubicacion_id
            
            # Verificar si la ubicación existe
            ubicacion_existente = self.db.ubicaciones.find_one({"_id": _id_obj})

            if not ubicacion_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"Ubicación con ID {ubicacion_id} no encontrada"
                return salida

            if ubicacion_existente.get("estatus") == "Cancelada":
                salida.estatus = "OK"
                salida.mensaje = f"La ubicación con ID {ubicacion_id} ya se encuentra cancelada"
                return salida

            # Verificar si la ubicación está siendo utilizada en asistencias
            asistencias_asociadas = self.db.asistencias.count_documents({
                "ubicacion_id": str(ubicacion_id),
                "estatus": {"$ne": "Cancelada"}
            })
            
            if asistencias_asociadas > 0:
                salida.estatus = "ERROR"
                salida.mensaje = "No se puede cancelar la ubicación porque tiene asistencias asociadas"
                return salida

            # Cancelar ubicación
            resultado = self.db.ubicaciones.update_one(
                {"_id": _id_obj},
                {"$set": {"estatus": "Cancelada"}}
            )

            if resultado.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Ubicación con ID {ubicacion_id} cancelada exitosamente"
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "La ubicación no se pudo cancelar. Verifique el estado actual"
                
        except Exception as ex:
            print(f"Error al cancelar ubicación {ubicacion_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al cancelar la ubicación"
            
        return salida