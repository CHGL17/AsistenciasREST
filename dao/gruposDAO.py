from models.gruposModel import GrupoInsert, GrupoUpdate, Salida, GrupoSelect, GruposSalida, GrupoSalida
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class GrupoDAO:
    def __init__(self, db):
        self.db = db
        
    def verificar_grupo_existente(self, grupo_id: str) -> bool:
        return self.db.grupos.find_one({"_id": ObjectId(grupo_id)}) is not None
        
    async def agregar(self, grupo: GrupoInsert) -> Salida:
        """Agregar un nuevo grupo"""
        salida = Salida(estatus="", mensaje="")
        try:
            # Validar existencia de ciclo, carrera y tutor
            ciclo = self.db.ciclos.find_one({"_id": ObjectId(grupo.ciclo)})
            if not ciclo:
                salida.estatus = "ERROR"
                salida.mensaje = "El ciclo especificado no existe"
                return salida
                
            carrera = self.db.carreras.find_one({"_id": grupo.carrera})
            if not carrera:
                salida.estatus = "ERROR"
                salida.mensaje = "La carrera especificada no existe"
                return salida
                
            tutor = self.db.usuarios.find_one({"_id": ObjectId(grupo.tutor), "tipo": "tutor"})
            if not tutor:
                salida.estatus = "ERROR"
                salida.mensaje = "El tutor especificado no existe o no es de tipo tutor"
                return salida
                
            # Validar existencia de alumnos
            alumnos_ids = [ObjectId(alumno_id) for alumno_id in grupo.alumnos]
            alumnos_count = self.db.usuarios.count_documents(
                {"_id": {"$in": alumnos_ids}, "tipo": "alumno"}
            )
            if alumnos_count != len(grupo.alumnos):
                salida.estatus = "ERROR"
                salida.mensaje = "Uno o más alumnos especificados no existen o no son de tipo alumno"
                return salida
                
            # Crear el grupo
            grupo_dict = jsonable_encoder(grupo)
            
            # Convertir IDs a ObjectId para inserción
            grupo_dict["ciclo"] = grupo.ciclo
            grupo_dict["carrera"] = grupo.carrera
            grupo_dict["tutor"] = grupo.tutor
            grupo_dict["alumnos"] = grupo.alumnos
            
            resultado = self.db.grupos.insert_one(grupo_dict)
            
            if resultado.inserted_id:
                grupo_creado = self.db.grupos.find_one({"_id": resultado.inserted_id})
                grupo_select = GrupoSelect(
                    id=str(grupo_creado["_id"]),
                    nombre=grupo_creado["nombre"],
                    semestre=grupo_creado["semestre"],
                    ciclo=str(grupo_creado["ciclo"]),
                    carrera=grupo_creado["carrera"],
                    tutor=str(grupo_creado["tutor"]),
                    alumnos=grupo_creado["alumnos"]
                )
                
                salida.estatus = "OK"
                salida.mensaje = f"Grupo creado con ID: {resultado.inserted_id}"
                return GrupoSalida(
                    estatus=salida.estatus,
                    mensaje=salida.mensaje,
                    grupo=grupo_select
                )
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "Error al crear el grupo"
                return salida
                
        except Exception as ex:
            print(f"Error al crear grupo: {ex}")
            salida.estatus = "ERROR" 
            salida.mensaje = "Error interno al agregar grupo."
            return salida
            
    async def consultaGeneral(self) -> GruposSalida:
        """Consultar todos los grupos"""
        salida = GruposSalida(estatus="", mensaje="", grupos=[])
        try:
            # Usar la vista viewGruposGeneral en lugar de la colección directa
            grupos_list = self.db.viewGruposGeneral.find()
            
            grupos = []
            for grupo in grupos_list:
                grupos.append(
                    GrupoSelect(
                        id=grupo["id"],
                        nombre=grupo["nombre"],
                        semestre=grupo["semestre"],
                        ciclo=grupo["ciclo"],  # Ahora es un objeto completo
                        carrera=grupo["carrera"],  # Ahora es un objeto completo
                        tutor=grupo["tutor"],  # Ahora es un objeto completo
                        alumnos=grupo["alumnos"]  # Ahora es una lista de objetos completos
                    )
                )
                
            salida.estatus = "OK"
            salida.mensaje = "Listado de grupos."
            salida.grupos = grupos
            
        except Exception as ex:
            print(f"Error al consultar grupos: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar los grupos, consulte al administrador."
            
        return salida

    async def consultarPorSemestre(self, semestre: int) -> GruposSalida:
        """Consultar grupos por semestre"""
        salida = GruposSalida(estatus="", mensaje="", grupos=[])
        try:
            # Usar la vista viewGruposGeneral con filtro por semestre
            grupos_list = self.db.viewGruposGeneral.find({"semestre": semestre})
            
            grupos = []
            for grupo in grupos_list:
                grupos.append(
                    GrupoSelect(
                        id=grupo["id"],
                        nombre=grupo["nombre"],
                        semestre=grupo["semestre"],
                        ciclo=grupo["ciclo"],  # Ahora es un objeto completo
                        carrera=grupo["carrera"],  # Ahora es un objeto completo
                        tutor=grupo["tutor"],  # Ahora es un objeto completo
                        alumnos=grupo["alumnos"]  # Ahora es una lista de objetos completos
                    )
                )
                
            salida.estatus = "OK"
            salida.mensaje = f"Grupos del semestre {semestre}."
            salida.grupos = grupos
            
        except Exception as ex:
            print(f"Error al consultar grupos por semestre {semestre}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar los grupos, consulte al administrador."
            
        return salida

    async def consultarPorID(self, grupo_id: str) -> GrupoSalida:
        """Consultar grupo por ID"""
        salida = GrupoSalida(estatus="", mensaje="", grupo=None)
        try:
            # Usar la vista viewGruposGeneral para consulta individual
            grupo = self.db.viewGruposGeneral.find_one({
                "$or": [
                    {"id": grupo_id},
                    {"_id": ObjectId(grupo_id)}
                ]
            })
            
            if not grupo:
                salida.estatus = "ERROR"
                salida.mensaje = f"Grupo con ID {grupo_id} no encontrado."
                return salida
                
            grupo_select = GrupoSelect(
                id=grupo["id"],
                nombre=grupo["nombre"],
                semestre=grupo["semestre"],
                ciclo=grupo["ciclo"],  # Ahora es un objeto completo
                carrera=grupo["carrera"],  # Ahora es un objeto completo
                tutor=grupo["tutor"],  # Ahora es un objeto completo
                alumnos=grupo["alumnos"]  # Ahora es una lista de objetos completos
            )
            
            salida.estatus = "OK"
            salida.mensaje = "Grupo encontrado."
            salida.grupo = grupo_select
            
        except Exception as ex:
            print(f"Error al consultar grupo {grupo_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar el grupo, consulte al administrador."
        return salida
        
    async def actualizar(self, grupo_id: str, grupo_update: GrupoUpdate) -> GrupoSalida:
        """Actualizar un grupo existente"""
        salida = GrupoSalida(estatus="", mensaje="", grupo=None)
        try:
            # Verificar si el grupo existe
            if not self.verificar_grupo_existente(grupo_id):
                salida.estatus = "ERROR"
                salida.mensaje = f"Grupo con ID {grupo_id} no encontrado."
                return salida
            
            # Preparar datos para actualización con validaciones
            update_data = {}
            for field, value in grupo_update.model_dump().items():
                if value is not None:
                    if field == "ciclo":
                        ciclo_id = value
                        if not self.db.ciclos.find_one({"_id": ciclo_id}):
                            salida.estatus = "ERROR"
                            salida.mensaje = "El ciclo especificado no existe"
                            return salida
                        update_data[field] = ciclo_id
                    elif field == "carrera":
                        if not self.db.carreras.find_one({"_id": value}):
                            salida.estatus = "ERROR"
                            salida.mensaje = "La carrera especificada no existe"
                            return salida
                        update_data[field] = value
                    elif field == "tutor":
                        tutor_id = ObjectId(value)
                        tutor = self.db.usuarios.find_one({"_id": tutor_id, "tipo": "tutor"})
                        if not tutor:
                            salida.estatus = "ERROR"
                            salida.mensaje = "El tutor especificado no existe o no es de tipo tutor"
                            return salida
                        update_data[field] = tutor_id
                    elif field == "alumnos":
                        alumnos_ids = [ObjectId(alumno_id) for alumno_id in value]
                        if self.db.usuarios.count_documents({"_id": {"$in": alumnos_ids}, "tipo": "alumno"}) != len(value):
                            salida.estatus = "ERROR"
                            salida.mensaje = "Uno o más alumnos especificados no existen o no son de tipo alumno"
                            return salida
                        update_data[field] = alumnos_ids
                    else:
                        update_data[field] = value
            
            # Si no hay campos para actualizar
            if not update_data:
                salida.estatus = "OK"
                salida.mensaje = "No se especificaron campos para actualizar."
                return salida
            
            # Realizar la actualización
            resultado = self.db.grupos.update_one(
                {"_id": ObjectId(grupo_id)},
                {"$set": update_data}
            )
            
            # Verificar si se realizaron cambios
            if resultado.modified_count > 0:
                grupo_actualizado = self.db.viewGruposGeneral.find_one({"_id": ObjectId(grupo_id)})
                grupo_select = GrupoSelect(
                    id=str(grupo_actualizado["_id"]),
                    nombre=grupo_actualizado["nombre"],
                    semestre=grupo_actualizado["semestre"],
                    ciclo=grupo_actualizado["ciclo"],
                    carrera=grupo_actualizado["carrera"],
                    tutor=grupo_actualizado["tutor"],
                    alumnos=[alumno for alumno in grupo_actualizado["alumnos"]]
                )
                salida.estatus = "OK"
                salida.mensaje = "Grupo actualizado correctamente."
                salida.grupo = grupo_select
            else:
                salida.estatus = "OK"
                salida.mensaje = "No se realizaron cambios en el grupo."
        
        except Exception as ex:
            print(f"Error al actualizar grupo {grupo_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar el grupo."
        
        return salida
            
    async def eliminar(self, grupo_id: str) -> Salida:
        """Eliminar un grupo"""
        salida = Salida(estatus="", mensaje="")
        try:
            # Verificar si el grupo existe
            if not self.verificar_grupo_existente(grupo_id):
                salida.estatus = "ERROR"
                salida.mensaje = f"Grupo con ID {grupo_id} no encontrado."
                return salida
            
            # Eliminar el grupo
            resultado = self.db.grupos.delete_one({"_id": ObjectId(grupo_id)})
            
            if resultado.deleted_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Grupo eliminado exitosamente. ID: {grupo_id}"
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "El grupo no se pudo eliminar."
        
        except Exception as ex:
            print(f"Error al eliminar grupo {grupo_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al eliminar el grupo."
        
        return salida
    
    async def agregarAlumno(self, grupo_id: str, alumno_id: str) -> GrupoSalida:
        """Agregar un alumno a un grupo existente"""
        try:
            # Validar que el grupo existe
            if not self.verificar_grupo_existente(grupo_id):
                return GrupoSalida(
                    estatus="ERROR",
                    mensaje=f"Grupo con ID {grupo_id} no encontrado",
                    grupo=None
                )

            # Validar que el alumno existe y es de tipo alumno
            alumno = self.db.usuarios.find_one({"_id": ObjectId(alumno_id), "tipo": "alumno"})
            if not alumno:
                return GrupoSalida(
                    estatus="ERROR",
                    mensaje="El alumno especificado no existe o no es de tipo alumno",
                    grupo=None
                )

            # Verificar si el alumno ya está en el grupo
            grupo_actual = self.db.grupos.find_one({"_id": ObjectId(grupo_id)})
            if alumno_id in [str(id) for id in grupo_actual.get("alumnos", [])]:
                return GrupoSalida(
                    estatus="ERROR",
                    mensaje="El alumno ya pertenece a este grupo",
                    grupo=None
                )

            # Agregar el alumno al array
            resultado = self.db.grupos.update_one(
                {"_id": ObjectId(grupo_id)},
                {"$addToSet": {"alumnos": ObjectId(alumno_id)}}
            )

            if resultado.modified_count > 0:
                # Retornar el grupo actualizado usando consultarPorID
                return await self.consultarPorID(grupo_id)
            else:
                return GrupoSalida(
                    estatus="ERROR",
                    mensaje="No se pudo agregar el alumno al grupo",
                    grupo=None
                )

        except Exception as ex:
            print(f"Error al agregar alumno al grupo: {ex}")
            return GrupoSalida(
                estatus="ERROR",
                mensaje="Error interno al agregar el alumno al grupo",
                grupo=None
            )

    async def eliminarAlumno(self, grupo_id: str, alumno_id: str) -> GrupoSalida:
        """Eliminar un alumno de un grupo existente"""
        try:
            # Validar que el grupo existe
            if not self.verificar_grupo_existente(grupo_id):
                return GrupoSalida(
                    estatus="ERROR",
                    mensaje=f"Grupo con ID {grupo_id} no encontrado",
                    grupo=None
                )

            # Validar que el alumno existe
            alumno = self.db.usuarios.find_one({"_id": ObjectId(alumno_id), "tipo": "alumno"})
            if not alumno:
                return GrupoSalida(
                    estatus="ERROR",
                    mensaje="El alumno especificado no existe o no es de tipo alumno",
                    grupo=None
                )

            # Verificar si el alumno está en el grupo
            grupo_actual = self.db.grupos.find_one({"_id": ObjectId(grupo_id)})
            if alumno_id not in [str(id) for id in grupo_actual.get("alumnos", [])]:
                return GrupoSalida(
                    estatus="ERROR",
                    mensaje="El alumno no pertenece a este grupo",
                    grupo=None
                )

            # Eliminar el alumno del array
            resultado = self.db.grupos.update_one(
                {"_id": ObjectId(grupo_id)},
                {"$pull": {"alumnos": ObjectId(alumno_id)}}
            )

            if resultado.modified_count > 0:
                # Retornar el grupo actualizado usando consultarPorID
                return await self.consultarPorID(grupo_id)
            else:
                return GrupoSalida(
                    estatus="ERROR",
                    mensaje="No se pudo eliminar el alumno del grupo",
                    grupo=None
                )

        except Exception as ex:
            print(f"Error al eliminar alumno del grupo: {ex}")
            return GrupoSalida(
                estatus="ERROR",
                mensaje="Error interno al eliminar el alumno del grupo",
                grupo=None
            )