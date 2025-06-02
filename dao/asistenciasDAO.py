from typing import List
from models.asistenciasModel import AsistenciaInsert, Salida, AsistenciaSelect, AsistenciaSalida, AsistenciasSalida
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from datetime import datetime, time, timedelta

class AsistenciaDAO:
    def __init__(self, db):
        self.db = db

    def verificar_actividad_existente(self, actividad_id: str) -> bool:
        """Verifica si existe la actividad especificada"""
        try:
            return self.db.actividades.find_one({"_id": ObjectId(actividad_id)}) is not None
        except:
            return False

    def verificar_ubicacion_existente(self, ubicacion_id: str) -> bool:
        """Verifica si existe la ubicación especificada"""
        try:
            return self.db.ubicaciones.find_one({"_id": ObjectId(ubicacion_id)}) is not None
        except:
            return False

    def verificar_grupo_existente(self, grupo_id: str) -> bool:
        """Verifica si existe el grupo especificado"""
        try:
            return self.db.grupos.find_one({"_id": ObjectId(grupo_id)}) is not None
        except:
            return False

    def verificar_alumnos_en_grupo(self, grupo_id: str, numeros_control: List[str]) -> bool:
        """Verifica que todos los números de control pertenezcan al grupo"""
        try:
            # Obtener alumnos del grupo
            grupo = self.db.grupos.find_one({"_id": ObjectId(grupo_id)})
            if not grupo:
                return False
            
            alumnos_grupo_ids = grupo.get("alumnos", [])
            # Verificar que todos los números de control pertenecen a alumnos del grupo
            alumnos_validos = self.db.usuarios.count_documents({
                "_id": {"$in": [ObjectId(alumno_id) for alumno_id in numeros_control if ObjectId(alumno_id) in alumnos_grupo_ids]},
                "tipo": "alumno"
            })
            
            return alumnos_validos == len(numeros_control)
        except Exception as ex:
            print(f"Error verificando alumnos en grupo: {ex}")
            return False

    def verificar_asistencia_existente(self, actividad_id: str, grupo_id: str, fecha_inicio: datetime) -> bool:
        """Verifica si ya existe una asistencia para la misma actividad, grupo y fecha"""
        try:
            # Convertir a ObjectId para la consulta
            # actividad_obj_id = 
            # grupo_obj_id = 
            
            # Extraer solo la fecha (sin hora) para comparación
            fecha_solo = fecha_inicio.date() # Sumar un día para incluir todo el día
            
            # Crear el rango de fechas para el día completo
            inicio_dia = datetime.combine(fecha_solo, time.min)
            fin_dia = datetime.combine(fecha_solo + timedelta(days=1), time.min)
            
            print(f"fecha: {fecha_solo}, inicio_dia: {inicio_dia}, fin_dia: {fin_dia}, actividad_id: {actividad_id}, grupo_id: {grupo_id}")
            
            # Buscar asistencias existentes para el mismo día, actividad y grupo
            asistencia_existente = self.db.asistencias.find_one({
                "actividad": ObjectId(actividad_id),
                "grupo": ObjectId(grupo_id),
                "fechaRegistro": {
                    "$gte": inicio_dia,
                    "$lt": fin_dia
                }
            })
            
            print(f"Asistencia existente: {asistencia_existente}")
            
            return asistencia_existente is not None
        except Exception as ex:
            print(f"Error verificando asistencia existente: {ex}")
            return False

    def verificar_asistencia_existente_por_id(self, asistencia_id: str) -> bool:
        """Verifica si existe la asistencia especificada por ID"""
        try:
            return self.db.asistencias.find_one({"_id": ObjectId(asistencia_id)}) is not None
        except:
            return False

    def verificar_alumno_existente(self, alumno_id: str) -> bool:
        """Verifica si existe el alumno especificado"""
        try:
            alumno = self.db.usuarios.find_one({"_id": ObjectId(alumno_id), "tipo": "alumno"})
            return alumno is not None
        except:
            return False

    def verificar_alumno_en_grupo_asistencia(self, asistencia_id: str, alumno_id: str) -> bool:
        """Verifica si el alumno pertenece al grupo de la asistencia"""
        try:
            # Obtener la asistencia
            asistencia = self.db.asistencias.find_one({"_id": ObjectId(asistencia_id)})
            if not asistencia:
                return False
            
            # Obtener el grupo de la asistencia
            grupo_id = asistencia.get("grupo")
            if not grupo_id:
                return False
            
            # Verificar si el alumno está en el grupo
            grupo = self.db.grupos.find_one({"_id": grupo_id})
            if not grupo:
                return False
            
            alumnos_grupo = [str(alumno_obj_id) for alumno_obj_id in grupo.get("alumnos", [])]
            return alumno_id in alumnos_grupo
            
        except Exception as ex:
            print(f"Error verificando alumno en grupo de asistencia: {ex}")
            return False

    def agregar(self, asistencia: AsistenciaInsert) -> AsistenciaSalida:
        """Agregar una nueva asistencia"""
        salida = AsistenciaSalida(estatus="", mensaje="", asistencia=None)
        
        try:
            # Validar que la actividad existe
            if not self.verificar_actividad_existente(asistencia.actividad):
                salida.estatus = "ERROR"
                salida.mensaje = "La actividad especificada no existe"
                return salida

            # Validar que la ubicación existe
            if not self.verificar_ubicacion_existente(asistencia.ubicacion):
                salida.estatus = "ERROR"
                salida.mensaje = "La ubicación especificada no existe"
                return salida

            # Validar que el grupo existe
            if not self.verificar_grupo_existente(asistencia.grupo):
                salida.estatus = "ERROR"
                salida.mensaje = "El grupo especificado no existe"
                return salida

            # Validar que los alumnos pertenecen al grupo
            if not self.verificar_alumnos_en_grupo(asistencia.grupo, asistencia.listaAsistencia):
                salida.estatus = "ERROR"
                salida.mensaje = "Uno o más números de control no pertenecen al grupo especificado"
                return salida

            # Validar que no existe asistencia duplicada
            if self.verificar_asistencia_existente(asistencia.actividad, asistencia.grupo, asistencia.fechaInicio):
                salida.estatus = "ERROR"
                salida.mensaje = "Ya existe una asistencia registrada para esta actividad, grupo y fecha"
                return salida

            # Validar que la fecha de fin sea posterior a la de inicio
            if asistencia.fechaFin <= asistencia.fechaInicio:
                salida.estatus = "ERROR"
                salida.mensaje = "La fecha de fin debe ser posterior a la fecha de inicio"
                return salida

            # Validar que la hora de fin sea posterior a la de inicio
            if asistencia.horaFin <= asistencia.horaInicio:
                salida.estatus = "ERROR"
                salida.mensaje = "La hora de fin debe ser posterior a la hora de inicio"
                return salida

            # Crear la asistencia
            asistencia_dict = jsonable_encoder(asistencia)
            
            # Convertir IDs a ObjectId
            asistencia_dict["actividad"] = ObjectId(asistencia.actividad)
            asistencia_dict["ubicacion"] = ObjectId(asistencia.ubicacion)
            asistencia_dict["grupo"] = ObjectId(asistencia.grupo)
            asistencia_dict["fechaRegistro"] = datetime.now()
            asistencia_dict["listaAsistencia"] = [
                {
                    "_id": ObjectId(alumno),
                    "fechaHoraRegistro": datetime.now()
                } for alumno in asistencia.listaAsistencia
            ]
            
            resultado = self.db.asistencias.insert_one(asistencia_dict)
            
            if resultado.inserted_id:
                # Obtener la asistencia creada desde la vista
                asistencia_creada = self.db.viewAsistenciasGeneral.find_one({"_id": resultado.inserted_id})
                
                if asistencia_creada:
                    asistencia_select = AsistenciaSelect(
                        id=str(asistencia_creada["_id"]),
                        actividad=asistencia_creada["actividad"],
                        fechaRegistro=asistencia_creada["fechaRegistro"],
                        fechaInicio=asistencia_creada["fechaInicio"],
                        fechaFin=asistencia_creada["fechaFin"],
                        horaInicio=asistencia_creada["horaInicio"],
                        horaFin=asistencia_creada["horaFin"],
                        estatus=asistencia_creada["estatus"],
                        ubicacion=asistencia_creada["ubicacion"],
                        grupo=asistencia_creada["grupo"],
                        listaAsistencia=asistencia_creada["listaAsistencia"]
                    )
                    
                    salida.estatus = "OK"
                    salida.mensaje = f"Asistencia registrada con ID: {resultado.inserted_id}"
                    salida.asistencia = asistencia_select
                else:
                    salida.estatus = "ERROR"
                    salida.mensaje = "Error al obtener la asistencia creada"
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "Error al registrar la asistencia"
                
        except Exception as ex:
            print(f"Error al registrar asistencia: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al registrar la asistencia"
            
        return salida

    def consultaGeneral(self) -> AsistenciasSalida:
        """Consultar todas las asistencias"""
        salida = AsistenciasSalida(estatus="", mensaje="", asistencias=[])
        
        try:
            asistencias_list = self.db.viewAsistenciasGeneral.find()
            
            asistencias = []
            for asistencia in asistencias_list:
                asistencias.append(
                    AsistenciaSelect(
                        id=str(asistencia["_id"]),
                        actividad=asistencia["actividad"],
                        fechaRegistro=asistencia["fechaRegistro"],
                        fechaInicio=asistencia["fechaInicio"],
                        fechaFin=asistencia["fechaFin"],
                        horaInicio=asistencia["horaInicio"],
                        horaFin=asistencia["horaFin"],
                        estatus=asistencia["estatus"],
                        ubicacion=asistencia["ubicacion"],
                        grupo=asistencia["grupo"],
                        listaAsistencia=asistencia["listaAsistencia"]
                    )
                )
                
            if not asistencias:
                salida.estatus = "ERROR"
                salida.mensaje = "No se encontró ningún dato registrado."
            else:
                salida.estatus = "OK"
                salida.mensaje = "Listado de asistencias."
                salida.asistencias = asistencias
                
        except Exception as ex:
            print(f"Error al consultar asistencias: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar las asistencias, consulte al administrador."
            
        return salida

    def agregarAlumnoAsistencia(self, asistencia_id: str, alumno_id: str) -> AsistenciaSalida:
        """Agregar un alumno a la lista de asistencia"""
        salida = AsistenciaSalida(estatus="", mensaje="", asistencia=None)
        
        try:
            # Validar que la asistencia existe
            if not self.verificar_asistencia_existente_por_id(asistencia_id):
                salida.estatus = "ERROR"
                salida.mensaje = f"Asistencia con ID {asistencia_id} no encontrada"
                return salida

            # Validar que el alumno existe
            if not self.verificar_alumno_existente(alumno_id):
                salida.estatus = "ERROR"
                salida.mensaje = "El alumno especificado no existe o no es de tipo alumno"
                return salida

            # Verificar que el alumno pertenece al grupo de la asistencia
            if not self.verificar_alumno_en_grupo_asistencia(asistencia_id, alumno_id):
                salida.estatus = "ERROR"
                salida.mensaje = "El alumno no pertenece al grupo de esta asistencia"
                return salida

            # Verificar si el alumno ya está en la lista de asistencia
            asistencia_actual = self.db.asistencias.find_one({"_id": ObjectId(asistencia_id)})
            alumnos_en_asistencia = [str(alumno["_id"]) for alumno in asistencia_actual.get("listaAsistencia", [])]
            
            if alumno_id in alumnos_en_asistencia:
                salida.estatus = "ERROR"
                salida.mensaje = "El alumno ya está registrado en esta asistencia"
                return salida

            # Agregar el alumno a la lista de asistencia
            resultado = self.db.asistencias.update_one(
                {"_id": ObjectId(asistencia_id)},
                {
                    "$addToSet": {
                        "listaAsistencia": {
                            "_id": ObjectId(alumno_id),
                            "fechaHoraRegistro": datetime.now()
                        }
                    }
                }
            )

            if resultado.modified_count > 0:
                # Obtener la asistencia actualizada desde la vista
                asistencia_actualizada = self.db.viewAsistenciasGeneral.find_one({"_id": ObjectId(asistencia_id)})
                
                if asistencia_actualizada:
                    asistencia_select = AsistenciaSelect(
                        id=str(asistencia_actualizada["_id"]),
                        actividad=asistencia_actualizada["actividad"],
                        fechaRegistro=asistencia_actualizada["fechaRegistro"],
                        fechaInicio=asistencia_actualizada["fechaInicio"],
                        fechaFin=asistencia_actualizada["fechaFin"],
                        horaInicio=asistencia_actualizada["horaInicio"],
                        horaFin=asistencia_actualizada["horaFin"],
                        estatus=asistencia_actualizada["estatus"],
                        ubicacion=asistencia_actualizada["ubicacion"],
                        grupo=asistencia_actualizada["grupo"],
                        listaAsistencia=asistencia_actualizada["listaAsistencia"]
                    )
                    
                    salida.estatus = "OK"
                    salida.mensaje = "Alumno agregado a la asistencia exitosamente"
                    salida.asistencia = asistencia_select
                else:
                    salida.estatus = "ERROR"
                    salida.mensaje = "Error al obtener la asistencia actualizada"
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo agregar el alumno a la asistencia"
                
        except Exception as ex:
            print(f"Error al agregar alumno a asistencia: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al agregar el alumno a la asistencia"
            
        return salida

    def eliminarAlumnoAsistencia(self, asistencia_id: str, alumno_id: str) -> AsistenciaSalida:
        """Eliminar un alumno de la lista de asistencia"""
        salida = AsistenciaSalida(estatus="", mensaje="", asistencia=None)
        
        try:
            # Validar que la asistencia existe
            if not self.verificar_asistencia_existente_por_id(asistencia_id):
                salida.estatus = "ERROR"
                salida.mensaje = f"Asistencia con ID {asistencia_id} no encontrada"
                return salida

            # Validar que el alumno existe
            if not self.verificar_alumno_existente(alumno_id):
                salida.estatus = "ERROR"
                salida.mensaje = "El alumno especificado no existe o no es de tipo alumno"
                return salida

            # Verificar si el alumno está en la lista de asistencia
            asistencia_actual = self.db.asistencias.find_one({"_id": ObjectId(asistencia_id)})
            alumnos_en_asistencia = [str(alumno["_id"]) for alumno in asistencia_actual.get("listaAsistencia", [])]
            
            if alumno_id not in alumnos_en_asistencia:
                salida.estatus = "ERROR"
                salida.mensaje = "El alumno no está registrado en esta asistencia"
                return salida

            # Eliminar el alumno de la lista de asistencia
            resultado = self.db.asistencias.update_one(
                {"_id": ObjectId(asistencia_id)},
                {
                    "$pull": {
                        "listaAsistencia": {
                            "_id": ObjectId(alumno_id)
                        }
                    }
                }
            )

            if resultado.modified_count > 0:
                # Obtener la asistencia actualizada desde la vista
                asistencia_actualizada = self.db.viewAsistenciasGeneral.find_one({"_id": ObjectId(asistencia_id)})
                
                if asistencia_actualizada:
                    asistencia_select = AsistenciaSelect(
                        id=str(asistencia_actualizada["_id"]),
                        actividad=asistencia_actualizada["actividad"],
                        fechaRegistro=asistencia_actualizada["fechaRegistro"],
                        fechaInicio=asistencia_actualizada["fechaInicio"],
                        fechaFin=asistencia_actualizada["fechaFin"],
                        horaInicio=asistencia_actualizada["horaInicio"],
                        horaFin=asistencia_actualizada["horaFin"],
                        estatus=asistencia_actualizada["estatus"],
                        ubicacion=asistencia_actualizada["ubicacion"],
                        grupo=asistencia_actualizada["grupo"],
                        listaAsistencia=asistencia_actualizada["listaAsistencia"]
                    )
                    
                    salida.estatus = "OK"
                    salida.mensaje = "Alumno eliminado de la asistencia exitosamente"
                    salida.asistencia = asistencia_select
                else:
                    salida.estatus = "ERROR"
                    salida.mensaje = "Error al obtener la asistencia actualizada"
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo eliminar el alumno de la asistencia"
                
        except Exception as ex:
            print(f"Error al eliminar alumno de asistencia: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al eliminar el alumno de la asistencia"
            
        return salida
    
    def consultarAsistenciaPorID(self, asistencia_id: str) -> AsistenciaSalida:
        """Consultar una asistencia específica por ID"""
        salida = AsistenciaSalida(estatus="", mensaje="", asistencia=None)
    
        try:
            # Validar que la asistencia existe
            if not self.verificar_asistencia_existente_por_id(asistencia_id):
                salida.estatus = "ERROR"
                salida.mensaje = f"Asistencia con ID {asistencia_id} no encontrada"
                return salida

            # Obtener la asistencia desde la vista
            asistencia = self.db.viewAsistenciasGeneral.find_one({"_id": ObjectId(asistencia_id)})
            
            if asistencia:
                asistencia_select = AsistenciaSelect(
                    id=str(asistencia["_id"]),
                    actividad=asistencia["actividad"],
                    fechaRegistro=asistencia["fechaRegistro"],
                    fechaInicio=asistencia["fechaInicio"],
                    fechaFin=asistencia["fechaFin"],
                    horaInicio=asistencia["horaInicio"],
                    horaFin=asistencia["horaFin"],
                    estatus=asistencia["estatus"],
                    ubicacion=asistencia["ubicacion"],
                    grupo=asistencia["grupo"],
                    listaAsistencia=asistencia["listaAsistencia"]
                )
                
                salida.estatus = "OK"
                salida.mensaje = "Asistencia encontrada exitosamente"
                salida.asistencia = asistencia_select
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "Error al obtener la asistencia"
                
        except Exception as ex:
            print(f"Error al consultar asistencia {asistencia_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al consultar la asistencia"
            
        return salida

    def actualizar(self, asistencia_id: str, asistencia_update: AsistenciaInsert) -> AsistenciaSalida:
        """Actualizar una asistencia existente"""
        salida = AsistenciaSalida(estatus="", mensaje="", asistencia=None)
        
        try:
            # Validar que la asistencia existe
            if not self.verificar_asistencia_existente_por_id(asistencia_id):
                salida.estatus = "ERROR"
                salida.mensaje = f"Asistencia con ID {asistencia_id} no encontrada"
                return salida

            # Validar que la actividad existe
            if not self.verificar_actividad_existente(asistencia_update.actividad):
                salida.estatus = "ERROR"
                salida.mensaje = "La actividad especificada no existe"
                return salida

            # Validar que la ubicación existe
            if not self.verificar_ubicacion_existente(asistencia_update.ubicacion):
                salida.estatus = "ERROR"
                salida.mensaje = "La ubicación especificada no existe"
                return salida

            # Validar que el grupo existe
            if not self.verificar_grupo_existente(asistencia_update.grupo):
                salida.estatus = "ERROR"
                salida.mensaje = "El grupo especificado no existe"
                return salida

            # Validar que los alumnos pertenecen al grupo
            if not self.verificar_alumnos_en_grupo(asistencia_update.grupo, asistencia_update.listaAsistencia):
                salida.estatus = "ERROR"
                salida.mensaje = "Uno o más números de control no pertenecen al grupo especificado"
                return salida

            # Validar que la fecha de fin sea posterior a la de inicio
            if asistencia_update.fechaFin <= asistencia_update.fechaInicio:
                salida.estatus = "ERROR"
                salida.mensaje = "La fecha de fin debe ser posterior a la fecha de inicio"
                return salida

            # Validar que la hora de fin sea posterior a la de inicio
            if asistencia_update.horaFin <= asistencia_update.horaInicio:
                salida.estatus = "ERROR"
                salida.mensaje = "La hora de fin debe ser posterior a la hora de inicio"
                return salida

            # Verificar duplicados (excluyendo la asistencia actual)
            asistencia_actual = self.db.asistencias.find_one({"_id": ObjectId(asistencia_id)})
            if (str(asistencia_actual.get("actividad")) != asistencia_update.actividad or 
                str(asistencia_actual.get("grupo")) != asistencia_update.grupo or 
                asistencia_actual.get("fechaInicio").date() != asistencia_update.fechaInicio.date()):
                
                if self.verificar_asistencia_existente(asistencia_update.actividad, asistencia_update.grupo, asistencia_update.fechaInicio):
                    salida.estatus = "ERROR"
                    salida.mensaje = "Ya existe una asistencia registrada para esta actividad, grupo y fecha"
                    return salida

            # Preparar datos para actualización
            update_data = {
                "actividad": ObjectId(asistencia_update.actividad),
                "fechaInicio": asistencia_update.fechaInicio,
                "fechaFin": asistencia_update.fechaFin,
                "horaInicio": asistencia_update.horaInicio,
                "horaFin": asistencia_update.horaFin,
                "estatus": asistencia_update.estatus,
                "ubicacion": ObjectId(asistencia_update.ubicacion),
                "grupo": ObjectId(asistencia_update.grupo),
                "listaAsistencia": [
                    {
                        "_id": ObjectId(alumno),
                        "fechaHoraRegistro": datetime.now()
                    } for alumno in asistencia_update.listaAsistencia
                ]
            }
            
            # Actualizar asistencia
            resultado = self.db.asistencias.update_one(
                {"_id": ObjectId(asistencia_id)},
                {"$set": update_data}
            )
            
            if resultado.modified_count > 0:
                # Obtener la asistencia actualizada desde la vista
                asistencia_actualizada = self.db.viewAsistenciasGeneral.find_one({"_id": ObjectId(asistencia_id)})
                
                if asistencia_actualizada:
                    asistencia_select = AsistenciaSelect(
                        id=str(asistencia_actualizada["_id"]),
                        actividad=asistencia_actualizada["actividad"],
                        fechaRegistro=asistencia_actualizada["fechaRegistro"],
                        fechaInicio=asistencia_actualizada["fechaInicio"],
                        fechaFin=asistencia_actualizada["fechaFin"],
                        horaInicio=asistencia_actualizada["horaInicio"],
                        horaFin=asistencia_actualizada["horaFin"],
                        estatus=asistencia_actualizada["estatus"],
                        ubicacion=asistencia_actualizada["ubicacion"],
                        grupo=asistencia_actualizada["grupo"],
                        listaAsistencia=asistencia_actualizada["listaAsistencia"]
                    )
                    
                    salida.estatus = "OK"
                    salida.mensaje = "Asistencia actualizada exitosamente"
                    salida.asistencia = asistencia_select
                else:
                    salida.estatus = "ERROR"
                    salida.mensaje = "Error al obtener la asistencia actualizada"
            else:
                salida.estatus = "OK"
                salida.mensaje = "No se realizaron cambios en la asistencia (posiblemente los datos ya eran los mismos)"
                # Devolver la asistencia actual
                asistencia_actual = self.db.viewAsistenciasGeneral.find_one({"_id": ObjectId(asistencia_id)})
                if asistencia_actual:
                    salida.asistencia = AsistenciaSelect(
                        id=str(asistencia_actual["_id"]),
                        actividad=asistencia_actual["actividad"],
                        fechaRegistro=asistencia_actual["fechaRegistro"],
                        fechaInicio=asistencia_actual["fechaInicio"],
                        fechaFin=asistencia_actual["fechaFin"],
                        horaInicio=asistencia_actual["horaInicio"],
                        horaFin=asistencia_actual["horaFin"],
                        estatus=asistencia_actual["estatus"],
                        ubicacion=asistencia_actual["ubicacion"],
                        grupo=asistencia_actual["grupo"],
                        listaAsistencia=asistencia_actual["listaAsistencia"]
                    )
                
        except Exception as ex:
            print(f"Error al actualizar asistencia {asistencia_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al actualizar la asistencia"
            
        return salida

    def cancelar(self, asistencia_id: str) -> Salida:
        """Cancelar/eliminar una asistencia (eliminación lógica)"""
        salida = Salida(estatus="", mensaje="")
        
        try:
            # Validar que la asistencia existe
            if not self.verificar_asistencia_existente_por_id(asistencia_id):
                salida.estatus = "ERROR"
                salida.mensaje = f"Asistencia con ID {asistencia_id} no encontrada"
                return salida

            # Verificar el estado actual de la asistencia
            asistencia_actual = self.db.asistencias.find_one({"_id": ObjectId(asistencia_id)})
            
            if asistencia_actual.get("estatus") == "Cancelada":
                salida.estatus = "OK"
                salida.mensaje = f"La asistencia con ID {asistencia_id} ya se encuentra cancelada"
                return salida

            # Cancelar la asistencia (cambio de estatus)
            resultado = self.db.asistencias.update_one(
                {"_id": ObjectId(asistencia_id)},
                {"$set": {"estatus": "Cancelada"}}
            )

            if resultado.modified_count > 0:
                salida.estatus = "OK"
                salida.mensaje = f"Asistencia con ID {asistencia_id} cancelada exitosamente"
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "No se pudo cancelar la asistencia. Verifique el estado actual"
                
        except Exception as ex:
            print(f"Error al cancelar asistencia {asistencia_id}: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al cancelar la asistencia"
            
        return salida