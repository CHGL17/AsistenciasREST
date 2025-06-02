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
            
            # Convertir IDs a ObjectId para inserción (CONSISTENCIA)
            grupo_dict["ciclo"] = ObjectId(grupo.ciclo)
            grupo_dict["carrera"] = grupo.carrera
            grupo_dict["tutor"] = ObjectId(grupo.tutor)
            grupo_dict["alumnos"] = alumnos_ids  # Ya convertidos a ObjectId arriba
            grupo_dict["estatus"] = "activo"
            
            resultado = self.db.grupos.insert_one(grupo_dict)
            
            if resultado.inserted_id:
                grupo_creado = self.db.viewGruposGeneral.find_one({"_id": resultado.inserted_id})
                grupo_select = GrupoSelect(
                    id=str(grupo_creado["_id"]),
                    nombre=grupo_creado["nombre"],
                    semestre=grupo_creado["semestre"],
                    ciclo=grupo_creado["ciclo"],
                    carrera=grupo_creado["carrera"],
                    tutor=grupo_creado["tutor"],
                    alumnos=grupo_creado["alumnos"],
                    estatus=grupo_creado["estatus"]
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
        """Consultar todos los grupos activos"""
        salida = GruposSalida(estatus="", mensaje="", grupos=[])
        try:
            # Filtrar solo grupos activos
            grupos_list = self.db.viewGruposGeneral.find({"estatus": "activo"})
            
            grupos = []
            for grupo in grupos_list:
                grupos.append(
                    GrupoSelect(
                        id=grupo["id"],
                        nombre=grupo["nombre"],
                        semestre=grupo["semestre"],
                        ciclo=grupo["ciclo"],
                        carrera=grupo["carrera"],
                        tutor=grupo["tutor"],
                        alumnos=grupo["alumnos"],
                        estatus=grupo["estatus"]
                    )
                )
                
            salida.estatus = "OK"
            salida.mensaje = "Listado de grupos activos."
            salida.grupos = grupos
            
        except Exception as ex:
            print(f"Error al consultar grupos: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar los grupos, consulte al administrador."
            
        return salida

    async def consultarPorSemestre(self, semestre: int) -> GruposSalida:
        """Consultar grupos activos por semestre"""
        salida = GruposSalida(estatus="", mensaje="", grupos=[])
        try:
            # Filtrar por semestre y solo grupos activos
            grupos_list = self.db.viewGruposGeneral.find({
                "semestre": semestre,
                "estatus": "activo"
            })
            
            grupos = []
            for grupo in grupos_list:
                grupos.append(
                    GrupoSelect(
                        id=grupo["id"],
                        nombre=grupo["nombre"],
                        semestre=grupo["semestre"],
                        ciclo=grupo["ciclo"],
                        carrera=grupo["carrera"],
                        tutor=grupo["tutor"],
                        alumnos=grupo["alumnos"],
                        estatus=grupo["estatus"]
                    )
                )
                
            salida.estatus = "OK"
            salida.mensaje = f"Grupos activos del semestre {semestre}."
            salida.grupos = grupos
            
        except Exception as ex:
            print(f"Error al consultar grupos por semestre {semestre}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar los grupos, consulte al administrador."
            
        return salida

    async def consultarPorID(self, grupo_id: str) -> GrupoSalida:
        """Consultar grupo por ID (incluye inactivos para permitir consulta completa)"""
        salida = GrupoSalida(estatus="", mensaje="", grupo=None)
        try:
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
                ciclo=grupo["ciclo"],
                carrera=grupo["carrera"],
                tutor=grupo["tutor"],
                alumnos=grupo["alumnos"],
                estatus=grupo["estatus"]
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
                        ciclo_id = ObjectId(value)  # Convertir a ObjectId
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
                        alumnos_ids = [ObjectId(alumno_id) for alumno_id in value]  # Convertir a ObjectId
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
                print(f"Grupo actualizado: {grupo_actualizado}")
                grupo_select = GrupoSelect(
                    id=grupo_actualizado["id"],
                    nombre=grupo_actualizado["nombre"],
                    semestre=grupo_actualizado["semestre"],
                    ciclo=grupo_actualizado["ciclo"],
                    carrera=grupo_actualizado["carrera"],
                    tutor=grupo_actualizado["tutor"],
                    alumnos=[alumno for alumno in grupo_actualizado["alumnos"]],
                    estatus=grupo_actualizado["estatus"]
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
        """Eliminar grupo de forma lógica (cambiar estatus a inactivo)"""
        salida = Salida(estatus="", mensaje="")
        try:
            # Verificar si el grupo existe y está activo
            grupo_existente = self.db.grupos.find_one({
                "_id": ObjectId(grupo_id),
                "estatus": "activo"
            })
            
            if not grupo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"Grupo con ID {grupo_id} no encontrado o ya está inactivo."
                return salida
            
            # Cambiar estatus a inactivo (eliminación lógica)
            resultado = self.db.grupos.update_one(
                {"_id": ObjectId(grupo_id)},
                {"$set": {"estatus": "inactivo"}}
            )
            
            if resultado.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Grupo desactivado exitosamente. ID: {grupo_id}"
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "El grupo no se pudo desactivar."
        
        except Exception as ex:
            print(f"Error al desactivar grupo {grupo_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al desactivar el grupo."
        
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
            
            # Convertir ObjectId a string para comparación consistente
            alumnos_en_grupo = [str(id) for id in grupo_actual.get("alumnos", [])]
            
            if alumno_id in alumnos_en_grupo:
                return GrupoSalida(
                    estatus="ERROR",
                    mensaje="El alumno ya pertenece a este grupo",
                    grupo=None
                )

            # Agregar el alumno al array como ObjectId
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
            
            # Convertir ObjectId a string para comparación consistente
            alumnos_en_grupo = [str(id) for id in grupo_actual.get("alumnos", [])]
            
            if alumno_id not in alumnos_en_grupo:
                return GrupoSalida(
                    estatus="ERROR",
                    mensaje="El alumno no pertenece a este grupo",
                    grupo=None
                )

            # Eliminar el alumno del array usando ObjectId
            resultado = self.db.grupos.update_one(
                {"_id": ObjectId(grupo_id)},
                {"$pull": {"alumnos": ObjectId(alumno_id)}}
            )
            
            print(f"Resultado de eliminar alumno: {resultado}")
            print(f"Modified count: {resultado.modified_count}")
            
            if resultado.modified_count > 0:
                # Retornar el grupo actualizado usando consultarPorID
                return await self.consultarPorID(grupo_id)
            else:
                # Debug adicional
                print(f"Debug - alumno_id: {alumno_id} (tipo: {type(alumno_id)})")
                print(f"Debug - alumnos en grupo: {alumnos_en_grupo}")
                print(f"Debug - ObjectId(alumno_id): {ObjectId(alumno_id)}")
                
                return GrupoSalida(
                    estatus="ERROR",
                    mensaje="No se pudo eliminar el alumno del grupo. Verifique que el alumno esté realmente en el grupo.",
                    grupo=None
                )

        except Exception as ex:
            print(f"Error al eliminar alumno del grupo: {ex}")
            return GrupoSalida(
                estatus="ERROR",
                mensaje="Error interno al eliminar el alumno del grupo",
                grupo=None
            )