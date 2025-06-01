from models.usuariosModel import (UsuarioAlumnoInsert, UsuarioTutorInsert, UsuarioCoordInsert, Salida,
                                  AlumnoResponse, TutorResponse, CoordinadorResponse,
                                  UsuarioSalidaID, UsuarioSalidaLista,
                                  )
from fastapi.encoders import jsonable_encoder
import bcrypt
import re
from datetime import datetime
from typing import Union, Dict, Any
from pymongo import MongoClient
from bson import ObjectId


class UsuarioDAO:
    def __init__(self, db: MongoClient):
        self.db = db
        self.usuarios = db.usuarios
        self.carreras = db.carreras

    # Valicación de campos y parámetros generales
    def _validar_carrera(self, carrera_id: int) -> bool:
        return self.carreras.find_one({"_id": carrera_id}) is not None

    def _validar_password(self, password: str) -> str | None:
        if len(password) < 8:
            return "La contraseña debe tener al menos 8 caracteres"
        if not any(c.isupper() for c in password):
            return "La contraseña debe contener al menos una mayúscula"
        if not any(c.isdigit() for c in password):
            return "La contraseña debe contener al menos un número"
        if not any(c in '!@#$%^&*()_+' for c in password):
            return "La contraseña debe contener al menos un carácter especial"
        return None

    def _validar_nombre_apellidos(self, nombre: str, apellidos: str) -> str | None:
        if not nombre or len(nombre.strip()) < 2:
            return "El nombre debe tener al menos 2 caracteres"
        if not re.match(r'^[A-Za-zÁ-ÿ\s]+$', nombre):
            return "El nombre solo puede contener letras y espacios"
        if not apellidos or len(apellidos.strip()) < 2:
            return "Los apellidos deben tener al menos 2 caracteres"
        if not re.match(r'^[A-Za-zÁ-ÿ\s]+$', apellidos):
            return "Los apellidos solo pueden contener letras y espacios"
        return None

    def _validar_nombre_carrera(self, carrera_id: int, nombre: str) -> bool:
        doc = self.carreras.find_one({"_id": carrera_id})
        return doc is not None and doc.get("nombre", "").strip().lower() == nombre.strip().lower()

    def agregarUsuario(self, usuario: Union[UsuarioAlumnoInsert, UsuarioTutorInsert, UsuarioCoordInsert]) -> Salida:
        try:
            error_nombre = self._validar_nombre_apellidos(usuario.nombre, usuario.apellidos)
            if error_nombre:
                return Salida(estatus="ERROR", mensaje=error_nombre)

            error_password = self._validar_password(usuario.password)
            if error_password:
                return Salida(estatus="ERROR", mensaje=error_password)

            if self.usuarios.find_one({"email": usuario.email}):
                return Salida(estatus="ERROR", mensaje="El correo electrónico ya está registrado")

            if isinstance(usuario, UsuarioAlumnoInsert):
                if not re.match(r'^\d{8}$', usuario.alumno.noControl):
                    return Salida(estatus="ERROR", mensaje="El número de control debe tener exactamente 8 dígitos")

                if usuario.alumno.semestre < 1 or usuario.alumno.semestre > 12:
                    return Salida(estatus="ERROR", mensaje="El semestre debe estar entre 1 y 12")

                if not self._validar_carrera(usuario.alumno.carrera):
                    return Salida(estatus="ERROR", mensaje="La carrera especificada no existe")

                if not self._validar_nombre_carrera(usuario.alumno.carrera, usuario.alumno.nombreCarrera):
                    return Salida(estatus="ERROR",
                                  mensaje="El nombre de la carrera del alumno no coincide con el ID proporcionado")

                if self.usuarios.find_one({"alumno.noControl": usuario.alumno.noControl}):
                    return Salida(estatus="ERROR", mensaje="El número de control ya está registrado")

                if not usuario.tutorId:
                    return Salida(estatus="ERROR", mensaje="Debe proporcionarse el ID del tutor")

                try:
                    tutor_oid = ObjectId(usuario.tutorId)
                except Exception:
                    return Salida(estatus="ERROR", mensaje="El ID del tutor no tiene un formato válido")

                tutor_doc = self.usuarios.find_one({
                    "_id": tutor_oid,
                    "tipo": "tutor",
                    "status": "activo"
                })

                if not tutor_doc:
                    return Salida(
                        estatus="ERROR",
                        mensaje="El tutor especificado no existe, no es válido o está inactivo"
                    )

                t = usuario.alumno.tutor
                if not t:
                    return Salida(estatus="ERROR", mensaje="Debe proporcionarse el objeto tutor embebido")

                if (
                        t.nombre != tutor_doc["nombre"]
                        or t.apellidos != tutor_doc["apellidos"]
                        or t.email != tutor_doc["email"]
                        or t.status != tutor_doc["status"]
                        or t.noDocente != tutor_doc["tutor"]["noDocente"]
                        or t.horasTutoria != tutor_doc["tutor"]["horasTutoria"]
                        or t.carrera != tutor_doc["tutor"]["carrera"]
                        or t.nombreCarrera != tutor_doc["tutor"]["nombreCarrera"]
                        or not self._validar_nombre_carrera(t.carrera, t.nombreCarrera)
                ):
                    return Salida(
                        estatus="ERROR",
                        mensaje="El objeto tutor embebido no coincide con el documento real del tutor"
                    )

            elif isinstance(usuario, UsuarioTutorInsert):
                if not re.match(r'^[A-Za-z]\d{4,9}$', usuario.tutor.noDocente):
                    return Salida(estatus="ERROR",
                                  mensaje="El número de docente debe comenzar con letra seguida de 4 a 9 dígitos")

                if usuario.tutor.horasTutoria < 1 or usuario.tutor.horasTutoria > 40:
                    return Salida(estatus="ERROR", mensaje="Las horas de tutoría deben estar entre 1 y 40")

                if not self._validar_carrera(usuario.tutor.carrera):
                    return Salida(estatus="ERROR", mensaje="La carrera especificada no existe")

                if not self._validar_nombre_carrera(usuario.tutor.carrera, usuario.tutor.nombreCarrera):
                    return Salida(estatus="ERROR",
                                  mensaje="El nombre de la carrera no coincide con el ID proporcionado")

                if self.usuarios.find_one({"tutor.noDocente": usuario.tutor.noDocente}):
                    return Salida(estatus="ERROR", mensaje="El número de docente ya está registrado")

            elif isinstance(usuario, UsuarioCoordInsert):
                if not re.match(r'^[A-Za-z]{2}\d{3,8}$', usuario.coordinador.noEmpleado):
                    return Salida(estatus="ERROR",
                                  mensaje="El número de empleado debe comenzar con 2 letras seguidas de 3 a 8 dígitos")

                if len(usuario.coordinador.departamento) < 3 or len(usuario.coordinador.departamento) > 50:
                    return Salida(estatus="ERROR", mensaje="El departamento debe tener entre 3 y 50 caracteres")

                if not self._validar_carrera(usuario.coordinador.carrera):
                    return Salida(estatus="ERROR", mensaje="La carrera especificada no existe")

                if not self._validar_nombre_carrera(usuario.coordinador.carrera, usuario.coordinador.nombreCarrera):
                    return Salida(estatus="ERROR",
                                  mensaje="El nombre de la carrera no coincide con el ID proporcionado")

                if self.usuarios.find_one({"coordinador.noEmpleado": usuario.coordinador.noEmpleado}):
                    return Salida(estatus="ERROR", mensaje="El número de empleado ya está registrado")

            hashed_password = bcrypt.hashpw(usuario.password.encode('utf-8'), bcrypt.gensalt())
            usuario_dict = usuario.model_dump(exclude={"password"})
            usuario_dict["password"] = hashed_password.decode("utf-8")
            usuario_dict["status"] = usuario.status

            if hasattr(usuario, "tutorId") and usuario.tutorId:
                usuario_dict["tutorId"] = ObjectId(usuario.tutorId)

            result = self.usuarios.insert_one(usuario_dict)

            return Salida(
                estatus="OK",
                mensaje=f"El usuario con ID {result.inserted_id} ha sido registrado exitosamente",
                id_usuario=str(result.inserted_id)
            )

        except Exception as ex:
            print(f"Error al registrar usuario: {str(ex)}")
            return Salida(estatus="ERROR", mensaje="Ocurrió un error interno al procesar el registro")

    # Componente DAO para la consulta individual (ID) de usuarios

    def consultarUsuarioPorID(self, id_usuario: str) -> UsuarioSalidaID:
        try:
            if not ObjectId.is_valid(id_usuario):
                return UsuarioSalidaID(
                    estatus="ERROR",
                    mensaje="ID de usuario no válido",
                    id_usuario=id_usuario
                )

            usuario_data = self.db.viewUsuariosID.find_one({
                "$or": [
                    {"id": id_usuario},
                    {"_id": ObjectId(id_usuario)}
                ]
            })

            if not usuario_data:
                return UsuarioSalidaID(
                    estatus="ERROR",
                    mensaje=f"Usuario con ID {id_usuario} no encontrado",
                    id_usuario=id_usuario
                )

            return UsuarioSalidaID(
                estatus="OK",
                mensaje="Usuario encontrado exitosamente",
                id_usuario=usuario_data.get("id", str(usuario_data.get("_id"))),
                usuario=usuario_data  # ← Devolver todo el documento ya enriquecido
            )

        except Exception as e:
            print(f"Error al consultar usuario {id_usuario}: {str(e)}")
            return UsuarioSalidaID(
                estatus="ERROR",
                mensaje="Error interno al consultar el usuario",
                id_usuario=id_usuario
            )

    # Componente DAO para la consulta general de usuarios

    def consultaGeneralUsuarios(self) -> UsuarioSalidaLista:
        salida = UsuarioSalidaLista(estatus="OK", mensaje="", usuarios=[])
        try:
            cursor = self.db.viewUsuariosGeneral.find()
            usuarios = []

            for usuario_data in cursor:
                tipo = usuario_data["tipo"]
                base_fields = {
                    "id": usuario_data["id"],
                    "email": usuario_data["email"],
                    "nombre": usuario_data["nombre"],
                    "apellidos": usuario_data["apellidos"],
                    "tipo": usuario_data["tipo"],
                    "status": usuario_data["status"],
                    "fechaRegistro": usuario_data["fechaRegistro"]
                }

                if tipo == "alumno":
                    usuario_resp = AlumnoResponse(**{
                        **base_fields,
                        "alumno": usuario_data["alumno"]
                    })
                    usuarios.append(usuario_resp)

                elif tipo == "tutor":
                    usuario_resp = TutorResponse(**{
                        **base_fields,
                        "tutor": usuario_data["tutor"]
                    })
                    usuarios.append(usuario_resp)

                elif tipo == "coordinador":
                    usuario_resp = CoordinadorResponse(**{
                        **base_fields,
                        "coordinador": usuario_data["coordinador"]
                    })
                    usuarios.append(usuario_resp)

            salida.mensaje = f"Se encontraron {len(usuarios)} usuarios"
            salida.usuarios = usuarios

        except Exception as ex:
            print(f"Error en consulta general: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error al obtener el listado de usuarios"

        return salida

    # Componente para la modificación de usuarios
    def actualizar_alumno(self, id_usuario: str, datos_actualizacion: dict, usuario_actual: dict) -> dict:
        usuario_existente = self.usuarios.find_one({"_id": ObjectId(id_usuario), "tipo": "alumno"})
        if not usuario_existente:
            return {
                "estatus": "ERROR",
                "mensaje": "El usuario no existe o no es un alumno",
                "status_code": 404
            }

        try:
            usuario = UsuarioAlumnoInsert(**datos_actualizacion)

            error_nombre = self._validar_nombre_apellidos(usuario.nombre, usuario.apellidos)
            if error_nombre:
                return {"estatus": "ERROR", "mensaje": error_nombre, "status_code": 400}

            error_password = self._validar_password(usuario.password)
            if error_password:
                return {"estatus": "ERROR", "mensaje": error_password, "status_code": 400}

            if not re.match(r'^\d{8}$', usuario.alumno.noControl):
                return {"estatus": "ERROR", "mensaje": "El número de control debe tener exactamente 8 dígitos",
                        "status_code": 400}

            if usuario.alumno.semestre < 1 or usuario.alumno.semestre > 12:
                return {"estatus": "ERROR", "mensaje": "El semestre debe estar entre 1 y 12", "status_code": 400}

            if not self._validar_carrera(usuario.alumno.carrera):
                return {"estatus": "ERROR", "mensaje": "La carrera especificada no existe", "status_code": 400}

            if not self._validar_nombre_carrera(usuario.alumno.carrera, usuario.alumno.nombreCarrera):
                return {"estatus": "ERROR", "mensaje": "El nombre de la carrera no coincide con el ID",
                        "status_code": 400}

            if usuario.tutorId:
                try:
                    tutor_oid = ObjectId(usuario.tutorId)
                except Exception:
                    return {"estatus": "ERROR", "mensaje": "El ID del tutor no tiene un formato válido",
                            "status_code": 400}

                tutor_doc = self.usuarios.find_one({"_id": tutor_oid, "tipo": "tutor"})

                if not tutor_doc:
                    return {"estatus": "ERROR",
                            "mensaje": "El tutor especificado no existe o no es válido",
                            "status_code": 400}

                t = usuario.alumno.tutor
                if not t:
                    return {"estatus": "ERROR", "mensaje": "Debe proporcionarse el objeto tutor embebido",
                            "status_code": 400}

                campos_tutor = ["nombre", "apellidos", "email", "noDocente", "horasTutoria", "carrera", "nombreCarrera",
                                "status"]
                for campo in campos_tutor:
                    if t.__dict__[campo] != (
                            tutor_doc["tutor"][campo] if campo not in ["nombre", "apellidos", "email", "status"] else
                            tutor_doc[campo]):
                        return {
                            "estatus": "ERROR",
                            "mensaje": f"El campo '{campo}' del tutor embebido no coincide con el tutor real",
                            "status_code": 400
                        }

            hashed_password = bcrypt.hashpw(usuario.password.encode('utf-8'), bcrypt.gensalt())
            usuario_dict = usuario.model_dump(exclude={"password"})
            usuario_dict["password"] = hashed_password.decode("utf-8")
            usuario_dict["fechaRegistro"] = datetime.now()
            if usuario.tutorId:
                usuario_dict["tutorId"] = ObjectId(usuario.tutorId)

            self.usuarios.update_one({"_id": ObjectId(id_usuario)}, {"$set": usuario_dict})

            # Actualizar status del tutor embebido si existe
            if usuario.tutorId:
                self.usuarios.update_many(
                    {
                        "tipo": "alumno",
                        "tutorId": ObjectId(usuario.tutorId),
                        "alumno.tutor": {"$exists": True}
                    },
                    {
                        "$set": {
                            "alumno.tutor.status": usuario.alumno.tutor.status
                        }
                    }
                )

            return {
                "estatus": "OK",
                "mensaje": "Alumno actualizado correctamente",
                "status_code": 200
            }

        except Exception as ex:
            print(f"Error al actualizar alumno: {ex}")
            return {
                "estatus": "ERROR",
                "mensaje": "Error interno al actualizar el alumno",
                "status_code": 500
            }

    # Se repite la lógica para TUTOR y COORDINADOR

    def actualizar_tutor(self, id_usuario: str, datos_actualizacion: dict, current_user: dict) -> dict:
        try:
            usuario = self.usuarios.find_one({"_id": ObjectId(id_usuario), "tipo": "tutor"})
            if not usuario:
                return {
                    "estatus": "ERROR",
                    "mensaje": "El usuario no existe o no es un tutor",
                    "status_code": 404
                }

            if error := self._validar_nombre_apellidos(datos_actualizacion.get("nombre", ""),
                                                       datos_actualizacion.get("apellidos", "")):
                return {"estatus": "ERROR", "mensaje": error, "status_code": 400}

            if error := self._validar_password(datos_actualizacion.get("password", "Hola123!")):
                return {"estatus": "ERROR", "mensaje": error, "status_code": 400}

            if "email" in datos_actualizacion:
                if self.usuarios.find_one(
                        {"email": datos_actualizacion["email"], "_id": {"$ne": ObjectId(id_usuario)}}):
                    return {"estatus": "ERROR", "mensaje": "El correo electrónico ya está registrado",
                            "status_code": 400}

            tutor_data = datos_actualizacion.get("tutor", {})
            if not tutor_data:
                return {"estatus": "ERROR", "mensaje": "Datos del tutor requeridos", "status_code": 400}

            if not re.match(r'^[A-Za-z]\d{4,9}$', tutor_data.get("noDocente", "")):
                return {"estatus": "ERROR",
                        "mensaje": "El número de docente debe comenzar con letra seguida de 4 a 9 dígitos",
                        "status_code": 400}

            if not 1 <= tutor_data.get("horasTutoria", 0) <= 40:
                return {"estatus": "ERROR", "mensaje": "Las horas de tutoría deben estar entre 1 y 40",
                        "status_code": 400}

            if not self._validar_carrera(tutor_data.get("carrera")):
                return {"estatus": "ERROR", "mensaje": "La carrera especificada no existe", "status_code": 400}

            if self.usuarios.find_one(
                    {"tutor.noDocente": tutor_data.get("noDocente"), "_id": {"$ne": ObjectId(id_usuario)}}):
                return {"estatus": "ERROR", "mensaje": "El número de docente ya está registrado", "status_code": 400}

            datos_actualizacion["fechaRegistro"] = datetime.now()
            if "password" in datos_actualizacion:
                datos_actualizacion["password"] = bcrypt.hashpw(datos_actualizacion["password"].encode("utf-8"),
                                                                bcrypt.gensalt()).decode("utf-8")

            self.usuarios.update_one({"_id": ObjectId(id_usuario)}, {"$set": datos_actualizacion})

            return {
                "estatus": "OK",
                "mensaje": "Tutor actualizado correctamente",
                "status_code": 200
            }

        except Exception as ex:
            print(f"Error al actualizar tutor {id_usuario}: {ex}")
            return {
                "estatus": "ERROR",
                "mensaje": "Error interno al actualizar el tutor",
                "status_code": 500
            }

    def actualizar_coordinador(self, id_usuario: str, datos_actualizacion: dict, current_user: dict) -> dict:
        try:
            usuario = self.usuarios.find_one({"_id": ObjectId(id_usuario), "tipo": "coordinador"})
            if not usuario:
                return {
                    "estatus": "ERROR",
                    "mensaje": "El usuario no existe o no es un coordinador",
                    "status_code": 404
                }

            if error := self._validar_nombre_apellidos(datos_actualizacion.get("nombre", ""),
                                                       datos_actualizacion.get("apellidos", "")):
                return {"estatus": "ERROR", "mensaje": error, "status_code": 400}

            if error := self._validar_password(datos_actualizacion.get("password", "Hola123!")):
                return {"estatus": "ERROR", "mensaje": error, "status_code": 400}

            if "email" in datos_actualizacion:
                if self.usuarios.find_one(
                        {"email": datos_actualizacion["email"], "_id": {"$ne": ObjectId(id_usuario)}}):
                    return {"estatus": "ERROR", "mensaje": "El correo electrónico ya está registrado",
                            "status_code": 400}

            coord_data = datos_actualizacion.get("coordinador", {})
            if not coord_data:
                return {"estatus": "ERROR", "mensaje": "Datos del coordinador requeridos", "status_code": 400}

            if not re.match(r'^[A-Za-z]{2}\d{3,8}$', coord_data.get("noEmpleado", "")):
                return {"estatus": "ERROR",
                        "mensaje": "El número de empleado debe comenzar con 2 letras seguidas de 3 a 8 dígitos",
                        "status_code": 400}

            if not (3 <= len(coord_data.get("departamento", "")) <= 50):
                return {"estatus": "ERROR", "mensaje": "El departamento debe tener entre 3 y 50 caracteres",
                        "status_code": 400}

            if not self._validar_carrera(coord_data.get("carrera")):
                return {"estatus": "ERROR", "mensaje": "La carrera especificada no existe", "status_code": 400}

            if self.usuarios.find_one(
                    {"coordinador.noEmpleado": coord_data.get("noEmpleado"), "_id": {"$ne": ObjectId(id_usuario)}}):
                return {"estatus": "ERROR", "mensaje": "El número de empleado ya está registrado", "status_code": 400}

            datos_actualizacion["fechaRegistro"] = datetime.now()
            if "password" in datos_actualizacion:
                datos_actualizacion["password"] = bcrypt.hashpw(datos_actualizacion["password"].encode("utf-8"),
                                                                bcrypt.gensalt()).decode("utf-8")

            self.usuarios.update_one({"_id": ObjectId(id_usuario)}, {"$set": datos_actualizacion})

            return {
                "estatus": "OK",
                "mensaje": "Coordinador actualizado correctamente",
                "status_code": 200
            }

        except Exception as ex:
            print(f"Error al actualizar coordinador {id_usuario}: {ex}")
            return {
                "estatus": "ERROR",
                "mensaje": "Error interno al actualizar el coordinador",
                "status_code": 500
            }

    # Componente para la eliminación de usuarios

    def eliminar_usuario_logico(self, id_usuario: str) -> Dict[str, Any]:
        try:
            if not ObjectId.is_valid(id_usuario):
                return {
                    "estatus": "ERROR",
                    "mensaje": "ID de usuario no válido",
                    "status_code": 400
                }

            usuario = self.usuarios.find_one({"_id": ObjectId(id_usuario)})
            if not usuario:
                return {
                    "estatus": "ERROR",
                    "mensaje": "Usuario no encontrado",
                    "status_code": 404
                }

            # Ya estaba inactivo
            if usuario.get("status") == "inactivo":
                return {
                    "estatus": "ERROR",
                    "mensaje": "El usuario ya se encuentra inactivo",
                    "status_code": 409
                }

            # Cambio de status del usuario raíz
            self.usuarios.update_one(
                {"_id": ObjectId(id_usuario)},
                {"$set": {"status": "inactivo"}}
            )

            # Si el usuario eliminado es un tutor, actualizar el status en todos los alumnos relacionados
            if usuario["tipo"] == "tutor":
                tutor_id = ObjectId(id_usuario)
                resultado = self.usuarios.update_many(
                    {
                        "tipo": "alumno",
                        "tutorId": tutor_id,
                        "alumno.tutor.nombre": usuario["nombre"],  # Esto ayuda a confirmar coincidencia exacta
                        "alumno.tutor.noDocente": usuario["tutor"]["noDocente"]
                    },
                    {
                        "$set": {
                            "alumno.tutor.status": "inactivo"
                        }
                    }
                )
                print(f"[+] Se actualizaron {resultado.modified_count} alumnos con tutor embebido inactivado.")

            return {
                "estatus": "OK",
                "mensaje": "El usuario fue desactivado exitosamente",
                "status_code": 200,
                "usuario_eliminado": self.formatear_usuario(usuario)
            }

        except Exception as ex:
            print(f"Error en eliminación lógica: {ex}")
            return {
                "estatus": "ERROR",
                "mensaje": "Error interno del servidor",
                "status_code": 500
            }

    def formatear_usuario(self, usuario: Dict) -> Dict:
        usuario_formateado = {
            "id": str(usuario["_id"]),
            "email": usuario["email"],
            "nombre": usuario["nombre"],
            "apellidos": usuario["apellidos"],
            "tipo": usuario["tipo"],
            "fechaRegistro": usuario["fechaRegistro"],
            "status": usuario.get("status", "activo")
        }

        if usuario["tipo"] == "alumno":
            usuario_formateado["alumno"] = usuario["alumno"]
        elif usuario["tipo"] == "tutor":
            usuario_formateado["tutor"] = usuario["tutor"]
        elif usuario["tipo"] == "coordinador":
            usuario_formateado["coordinador"] = usuario["coordinador"]

        return usuario_formateado
