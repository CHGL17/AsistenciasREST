from models.actividadesModel import ActividadInsert, Salida, ActividadesSalida, ActividadSelectID, ActividadesSalidaID, TutorInfo, TutorAsignacion
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class ActividadDAO:
    def __init__(self, db):
        self.db = db

    def _obtener_tutor_info(self, tutor_id: str) -> TutorInfo:
        """
        Obtiene la información del tutor por su ID desde la colección de usuarios
        """
        try:
            _id_obj = ObjectId(tutor_id) if ObjectId.is_valid(tutor_id) else tutor_id
            # Buscar en la colección de usuarios, filtrando por tipo "tutor"
            usuario_tutor = self.db.usuarios.find_one({
                "_id": _id_obj,
                "tipo": "tutor"
            })
            if usuario_tutor:
                return TutorInfo(
                    id=str(usuario_tutor["_id"]),
                    nombre=f"{usuario_tutor['nombre']} {usuario_tutor['apellidos']}"
                )
            else:
                return TutorInfo(id=str(tutor_id), nombre="Tutor no encontrado")
        except Exception:
            return TutorInfo(id=str(tutor_id), nombre="Error al obtener tutor")
    
    def agregar(self, actividad: ActividadInsert):
        salida = Salida(estatus="", mensaje="")
        try:
            # Verificar si ya existe una actividad con el mismo nombre
            actividad_existente = self.db.actividades.find_one({"nombre": actividad.nombre})
            if actividad_existente:
                salida.estatus = "ERROR"
                salida.mensaje = "Ya existe una actividad con este nombre."
                return salida

            # Si se proporciona un tutor_id, verificar que existe y es de tipo tutor
            if hasattr(actividad, 'tutor_id') and actividad.tutor_id:
                tutor_valido = self.db.usuarios.find_one({
                    "_id": ObjectId(actividad.tutor_id),
                    "tipo": "tutor",
                    "status": "activo"
                })
                if not tutor_valido:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"El usuario con ID {actividad.tutor_id} no es un tutor válido o no está activo."
                    return salida

            nueva_actividad = jsonable_encoder(actividad)
            resultado = self.db.actividades.insert_one(nueva_actividad)
            
            if resultado.inserted_id:
                actividad_creada = self.db.actividades.find_one({"_id": resultado.inserted_id})
                
                # Obtener información del tutor si existe
                tutor_info = None
                if actividad_creada.get("tutor_id"):
                    tutor_info = self._obtener_tutor_info(actividad_creada["tutor_id"])
                
                actividad_select = ActividadSelectID(
                    id=str(actividad_creada["_id"]),
                    nombre=actividad_creada["nombre"],
                    descripcion=actividad_creada["descripcion"],
                    estatus=actividad_creada["estatus"],
                    obligatoria=actividad_creada["obligatoria"],
                    tutor=tutor_info
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
                # Obtener información del tutor si existe
                tutor_info = None
                if actividad.get("tutor_id"):
                    tutor_info = self._obtener_tutor_info(actividad["tutor_id"])
                
                actividades.append(
                    ActividadSelectID(
                        id=str(actividad["_id"]),
                        nombre=actividad["nombre"],
                        descripcion=actividad["descripcion"],
                        estatus=actividad["estatus"],
                        obligatoria=actividad["obligatoria"],
                        tutor=tutor_info
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
            
            # Obtener información del tutor si existe
            tutor_info = None
            if actividad.get("tutor_id"):
                tutor_info = self._obtener_tutor_info(actividad["tutor_id"])
            
            actividad_select = ActividadSelectID(
                id=str(actividad["_id"]),
                nombre=actividad["nombre"],
                descripcion=actividad["descripcion"],
                estatus=actividad["estatus"],
                obligatoria=actividad["obligatoria"],
                tutor=tutor_info
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
            
            # Verificar nombres duplicados
            actividad_existente_mismo_nombre = self.db.actividades.find_one({
                "nombre": actividad_update.nombre,
                "_id": {"$ne": _id_obj}
            })
            if actividad_existente_mismo_nombre:
                salida.estatus = "ERROR"
                salida.mensaje = f"Ya existe otra actividad con el nombre '{actividad_update.nombre}'."
                return salida

            # Verificar que la actividad existe
            actividad_existente = self.db.actividades.find_one({"_id": _id_obj})
            if not actividad_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"Actividad con ID {actividad_id} no encontrada."
                return salida

            # Si se proporciona un tutor_id, verificar que es válido
            if hasattr(actividad_update, 'tutor_id') and actividad_update.tutor_id:
                tutor_valido = self.db.usuarios.find_one({
                    "_id": ObjectId(actividad_update.tutor_id),
                    "tipo": "tutor",
                    "status": "activo"
                })
                if not tutor_valido:
                    salida.estatus = "ERROR"
                    salida.mensaje = f"El usuario con ID {actividad_update.tutor_id} no es un tutor válido o no está activo."
                    return salida

            actividad_dict = actividad_update.model_dump()
            update_data = {
                "nombre": actividad_dict["nombre"],
                "descripcion": actividad_dict["descripcion"],
                "estatus": actividad_dict["estatus"],
                "obligatoria": actividad_dict["obligatoria"]
            }
            
            # Solo agregar tutor_id si está presente
            if actividad_dict.get("tutor_id"):
                update_data["tutor_id"] = actividad_dict["tutor_id"]

            resultado = self.db.actividades.update_one(
                {"_id": _id_obj},
                {"$set": update_data}
            )
            
            if resultado.modified_count > 0:
                actividad_actualizada = self.db.actividades.find_one({"_id": _id_obj})
                
                # Obtener información del tutor si existe
                tutor_info = None
                if actividad_actualizada.get("tutor_id"):
                    tutor_info = self._obtener_tutor_info(actividad_actualizada["tutor_id"])
                
                actividad_select = ActividadSelectID(
                    id=str(actividad_actualizada["_id"]),
                    nombre=actividad_actualizada["nombre"],
                    descripcion=actividad_actualizada["descripcion"],
                    estatus=actividad_actualizada["estatus"],
                    obligatoria=actividad_actualizada["obligatoria"],
                    tutor=tutor_info
                )
                salida.estatus = "OK"
                salida.mensaje = "Actividad actualizada correctamente."
                salida.actividad = actividad_select
            else:
                salida.estatus = "OK"
                salida.mensaje = "No se realizaron cambios en la actividad (posiblemente los datos ya eran los mismos)."
                actividad_actual = self.db.actividades.find_one({"_id": _id_obj})
                if actividad_actual:
                    tutor_info = None
                    if actividad_actual.get("tutor_id"):
                        tutor_info = self._obtener_tutor_info(actividad_actual["tutor_id"])
                    
                    salida.actividad = ActividadSelectID(
                        id=str(actividad_actual["_id"]),
                        nombre=actividad_actual["nombre"],
                        descripcion=actividad_actual["descripcion"],
                        estatus=actividad_actual["estatus"],
                        obligatoria=actividad_actual["obligatoria"],
                        tutor=tutor_info
                    )
        except Exception as ex:
            print(f"Error al actualizar actividad {actividad_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar la actividad."
        return salida
    
    def asignar_tutor(self, actividad_id: str, tutor_asignacion: TutorAsignacion) -> ActividadesSalidaID:
        """
        Asigna un tutor a una actividad específica
        """
        salida = ActividadesSalidaID(estatus="", mensaje="", actividad=None)
        try:
            _id_obj = ObjectId(actividad_id) if ObjectId.is_valid(actividad_id) else actividad_id
            
            # Verificar que la actividad existe
            actividad_existente = self.db.actividades.find_one({"_id": _id_obj})
            if not actividad_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"Actividad con ID {actividad_id} no encontrada."
                return salida

            # Verificar que la actividad no esté cancelada
            if actividad_existente.get("estatus") == "Cancelada":
                salida.estatus = "ERROR"
                salida.mensaje = "No se puede asignar tutor a una actividad cancelada."
                return salida

            # Verificar que el usuario existe, es de tipo tutor y está activo
            tutor_id_obj = ObjectId(tutor_asignacion.tutor_id) if ObjectId.is_valid(tutor_asignacion.tutor_id) else tutor_asignacion.tutor_id
            usuario_tutor = self.db.usuarios.find_one({
                "_id": tutor_id_obj,
                "tipo": "tutor",
                "status": "activo"
            })
            
            if not usuario_tutor:
                salida.estatus = "ERROR"
                salida.mensaje = f"El usuario con ID {tutor_asignacion.tutor_id} no es un tutor válido o no está activo."
                return salida

            # Verificar si ya tiene el mismo tutor asignado
            tutor_actual = actividad_existente.get("tutor_id")
            if tutor_actual == tutor_asignacion.tutor_id:
                salida.estatus = "OK"
                salida.mensaje = "El tutor ya está asignado a esta actividad."
                tutor_info = self._obtener_tutor_info(tutor_asignacion.tutor_id)
                salida.actividad = ActividadSelectID(
                    id=str(actividad_existente["_id"]),
                    nombre=actividad_existente["nombre"],
                    descripcion=actividad_existente["descripcion"],
                    estatus=actividad_existente["estatus"],
                    obligatoria=actividad_existente["obligatoria"],
                    tutor=tutor_info
                )
                return salida

            # Asignar el nuevo tutor
            resultado = self.db.actividades.update_one(
                {"_id": _id_obj},
                {"$set": {"tutor_id": tutor_asignacion.tutor_id}}
            )

            if resultado.modified_count > 0:
                # Obtener la actividad actualizada
                actividad_actualizada = self.db.actividades.find_one({"_id": _id_obj})
                tutor_info = self._obtener_tutor_info(actividad_actualizada["tutor_id"])
                
                actividad_select = ActividadSelectID(
                    id=str(actividad_actualizada["_id"]),
                    nombre=actividad_actualizada["nombre"],
                    descripcion=actividad_actualizada["descripcion"],
                    estatus=actividad_actualizada["estatus"],
                    obligatoria=actividad_actualizada["obligatoria"],
                    tutor=tutor_info
                )
                
                tutor_nombre = f"{usuario_tutor['nombre']} {usuario_tutor['apellidos']}"
                salida.estatus = "OK"
                salida.mensaje = f"Tutor {tutor_nombre} asignado exitosamente a la actividad."
                salida.actividad = actividad_select
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo asignar el tutor. Intente nuevamente."
                
        except Exception as ex:
            print(f"Error al asignar tutor a actividad {actividad_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al asignar el tutor."
            
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