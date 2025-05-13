from models.gruposModel import GrupoInsert, Salida, GrupoSelect, GruposSalida, GrupoSalida
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class GrupoDAO:
    def __init__(self, db):
        self.db = db
        
    async def agregar(self, grupo: GrupoInsert) -> Salida:
        """Agregar un nuevo grupo"""
        salida = Salida(estatus="", mensaje="")
        try:
            # Validar existencia de ciclo, carrera y tutor
            ciclo = self.db.ciclos.find_one({"_id": grupo.ciclo})
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
            # grupos_cursor = self.db.grupos.find()
            grupos_list = self.db.grupos.find()
            
            if not grupos_list:
                salida.estatus = "ERROR"
                salida.mensaje = "No se encontró ningún grupo registrado."
                return salida
                
            grupos = []
            for grupo in grupos_list:
                grupos.append(
                    GrupoSelect(
                        id=str(grupo["_id"]),
                        nombre=grupo["nombre"],
                        semestre=grupo["semestre"],
                        ciclo=str(grupo["ciclo"]),
                        carrera=str(grupo["carrera"]),
                        tutor=str(grupo["tutor"]),
                        alumnos=[str(alumno) for alumno in grupo["alumnos"]]
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
            grupos_list = self.db.grupos.find({"semestre": semestre})
            
            if not grupos_list:
                salida.estatus = "ERROR"
                salida.mensaje = f"No se encontraron grupos para el semestre {semestre}."
                return salida
                
            grupos = []
            for grupo in grupos_list:
                grupos.append(
                    GrupoSelect(
                        id=str(grupo["_id"]),
                        nombre=grupo["nombre"],
                        semestre=grupo["semestre"],
                        ciclo=str(grupo["ciclo"]),
                        carrera=str(grupo["carrera"]),
                        tutor=str(grupo["tutor"]),
                        alumnos=[str(alumno) for alumno in grupo["alumnos"]]
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
            grupo = self.db.grupos.find_one({"_id": grupo_id})
            print(grupo)
            
            if not grupo:
                salida.estatus = "ERROR"
                salida.mensaje = f"Grupo con ID {grupo_id} no encontrado."
                return salida
                
            grupo_select = GrupoSelect(
                id=str(grupo["_id"]),
                nombre=grupo["nombre"],
                semestre=grupo["semestre"],
                ciclo=str(grupo["ciclo"]),
                carrera=str(grupo["carrera"]),
                tutor=str(grupo["tutor"]),
                alumnos=[str(alumno) for alumno in grupo["alumnos"]]
            )
            
            salida.estatus = "OK"
            salida.mensaje = "Grupo encontrado."
            salida.grupo = grupo_select
            
        except Exception as ex:
            print(f"Error al consultar grupo {grupo_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar el grupo, consulte al administrador."
            
        return salida
        
    async def actualizar(self, grupo_id: str, grupo_update: GrupoInsert) -> GrupoSalida:
        """Actualizar un grupo existente"""
        salida = GrupoSalida(estatus="", mensaje="", grupo=None)
        try:
            # Verificar que el grupo existe
            grupo_existente = self.db.grupos.find_one({"_id": ObjectId(grupo_id)})
            if not grupo_existente:
                salida.estatus = "ERROR"
                salida.mensaje = f"Grupo con ID {grupo_id} no encontrado."
                return salida
            
            # Validar existencia de ciclo, carrera y tutor
            ciclo = self.db.ciclos.find_one({"_id": ObjectId(grupo_update.ciclo)})
            if not ciclo:
                salida.estatus = "ERROR"
                salida.mensaje = "El ciclo especificado no existe"
                return salida
                
            carrera = self.db.carreras.find_one({"_id": grupo_update.carrera})
            if not carrera:
                salida.estatus = "ERROR"
                salida.mensaje = "La carrera especificada no existe"
                return salida
                
            tutor = self.db.usuarios.find_one({"_id": ObjectId(grupo_update.tutor), "tipo": "tutor"})
            if not tutor:
                salida.estatus = "ERROR"
                salida.mensaje = "El tutor especificado no existe o no es de tipo tutor"
                return salida
                
            # Validar existencia de alumnos
            alumnos_ids = [ObjectId(alumno_id) for alumno_id in grupo_update.alumnos]
            alumnos_count = self.db.usuarios.count_documents(
                {"_id": {"$in": alumnos_ids}, "tipo": "alumno"}
            )
            if alumnos_count != len(grupo_update.alumnos):
                salida.estatus = "ERROR"
                salida.mensaje = "Uno o más alumnos especificados no existen o no son de tipo alumno"
                return salida
                
            # Preparar datos para actualización
            grupo_dict = grupo_update.dict()
            update_data = {
                "nombre": grupo_dict["nombre"],
                "semestre": grupo_dict["semestre"],
                "ciclo": ObjectId(grupo_dict["ciclo"]),
                "carrera": ObjectId(grupo_dict["carrera"]),
                "tutor": ObjectId(grupo_dict["tutor"]),
                "alumnos": alumnos_ids
            }
            
            # Actualizar el grupo
            resultado = self.db.grupos.update_one(
                {"_id": ObjectId(grupo_id)},
                {"$set": update_data}
            )
            
            if resultado.modified_count > 0:
                # Obtener el grupo actualizado
                grupo_actualizado = self.db.grupos.find_one({"_id": ObjectId(grupo_id)})
                
                grupo_select = GrupoSelect(
                    id=str(grupo_actualizado["_id"]),
                    nombre=grupo_actualizado["nombre"],
                    semestre=grupo_actualizado["semestre"],
                    ciclo=str(grupo_actualizado["ciclo"]),
                    carrera=str(grupo_actualizado["carrera"]),
                    tutor=str(grupo_actualizado["tutor"]),
                    alumnos=[str(alumno) for alumno in grupo_actualizado["alumnos"]]
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
            # Verificar que el grupo existe
            grupo_existente = self.db.grupos.find_one({"_id": ObjectId(grupo_id)})
            if not grupo_existente:
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