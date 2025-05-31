from models.usuariosModel import (UsuarioAlumnoInsert, UsuarioTutorInsert, UsuarioCoordInsert, Salida, AlumnoModel,
                                  TutorModel, CoordinadorModel, AlumnoResponse, TutorResponse, CoordinadorResponse,
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

    def agregarUsuario(
            self,
            usuario: Union[UsuarioAlumnoInsert, UsuarioTutorInsert, UsuarioCoordInsert]
    ) -> Salida:
        try:
            # Validaciones generales
            error_nombre = self._validar_nombre_apellidos(usuario.nombre, usuario.apellidos)
            if error_nombre:
                return Salida(estatus="ERROR", mensaje=error_nombre)

            error_password = self._validar_password(usuario.password)
            if error_password:
                return Salida(estatus="ERROR", mensaje=error_password)

            # Validar email único
            if self.usuarios.find_one({"email": usuario.email}):
                return Salida(
                    estatus="ERROR",
                    mensaje="El correo electrónico ya está registrado"
                )

            # Validaciones específicas por tipo
            if isinstance(usuario, UsuarioAlumnoInsert):
                if not re.match(r'^\d{8}$', usuario.alumno.noControl):
                    return Salida(
                        estatus="ERROR",
                        mensaje="El número de control debe tener exactamente 8 dígitos"
                    )

                if usuario.alumno.semestre < 1 or usuario.alumno.semestre > 12:
                    return Salida(
                        estatus="ERROR",
                        mensaje="El semestre debe estar entre 1 y 12"
                    )

                if not self._validar_carrera(usuario.alumno.carrera):
                    return Salida(
                        estatus="ERROR",
                        mensaje="La carrera especificada no existe"
                    )

                if self.usuarios.find_one({"alumno.noControl": usuario.alumno.noControl}):
                    return Salida(
                        estatus="ERROR",
                        mensaje="El número de control ya está registrado"
                    )

                tutor_doc = None
                if hasattr(usuario, "tutorId") and usuario.tutorId:
                    try:
                        tutor_oid = ObjectId(usuario.tutorId)
                    except Exception:
                        return Salida(
                            estatus="ERROR",
                            mensaje="El ID del tutor no tiene un formato válido"
                        )

                    tutor_doc = self.usuarios.find_one({
                        "_id": tutor_oid,
                        "tipo": "tutor"
                    })
                    if not tutor_doc:
                        return Salida(
                            estatus="ERROR",
                            mensaje="El tutor especificado no existe o no es válido"
                        )

            elif isinstance(usuario, UsuarioTutorInsert):
                if not re.match(r'^[A-Za-z]\d{4,9}$', usuario.tutor.noDocente):
                    return Salida(
                        estatus="ERROR",
                        mensaje="El número de docente debe comenzar con letra seguida de 4 a 9 dígitos"
                    )

                if usuario.tutor.horasTutoria < 1 or usuario.tutor.horasTutoria > 40:
                    return Salida(
                        estatus="ERROR",
                        mensaje="Las horas de tutoría deben estar entre 1 y 40"
                    )

                if not self._validar_carrera(usuario.tutor.carrera):
                    return Salida(
                        estatus="ERROR",
                        mensaje="La carrera especificada no existe"
                    )

                if self.usuarios.find_one({"tutor.noDocente": usuario.tutor.noDocente}):
                    return Salida(
                        estatus="ERROR",
                        mensaje="El número de docente ya está registrado"
                    )

            elif isinstance(usuario, UsuarioCoordInsert):
                if not re.match(r'^[A-Za-z]{2}\d{3,8}$', usuario.coordinador.noEmpleado):
                    return Salida(
                        estatus="ERROR",
                        mensaje="El número de empleado debe comenzar con 2 letras seguidas de 3 a 8 dígitos"
                    )

                if len(usuario.coordinador.departamento) < 3 or len(usuario.coordinador.departamento) > 50:
                    return Salida(
                        estatus="ERROR",
                        mensaje="El departamento debe tener entre 3 y 50 caracteres"
                    )

                if not self._validar_carrera(usuario.coordinador.carrera):
                    return Salida(
                        estatus="ERROR",
                        mensaje="La carrera especificada no existe"
                    )

                if self.usuarios.find_one({"coordinador.noEmpleado": usuario.coordinador.noEmpleado}):
                    return Salida(
                        estatus="ERROR",
                        mensaje="El número de empleado ya está registrado"
                    )

            # Hashear la contraseña
            hashed_password = bcrypt.hashpw(
                usuario.password.encode('utf-8'),
                bcrypt.gensalt()
            )

            # Preparar documento para MongoDB
            usuario_dict = usuario.model_dump(exclude={"password"})
            usuario_dict["password"] = hashed_password.decode("utf-8")
            if tutor_doc:
                usuario_dict["tutorId"] = tutor_doc["_id"]

            # Insertar en la base de datos
            result = self.usuarios.insert_one(usuario_dict)

            return Salida(
                estatus="OK",
                mensaje=f"El usuario con ID {result.inserted_id} ha sido registrado exitosamente",
                id_usuario=str(result.inserted_id)
            )

        except Exception as ex:
            print(f"Error al registrar usuario: {str(ex)}")
            return Salida(
                estatus="ERROR",
                mensaje="Ocurrió un error interno al procesar el registro"
            )

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
        usuario = self.usuarios.find_one({"_id": ObjectId(id_usuario), "tipo": "alumno"})
        if not usuario:
            return {
                "estatus": "ERROR",
                "mensaje": "El usuario no existe o no es un alumno",
                "status_code": 404
            }

        return self._actualizar_usuario_generico(id_usuario, datos_actualizacion, usuario_actual, "alumno")

    def actualizar_tutor(self, id_usuario: str, datos_actualizacion: dict, usuario_actual: dict) -> dict:
        usuario = self.usuarios.find_one({"_id": ObjectId(id_usuario), "tipo": "tutor"})
        if not usuario:
            return {
                "estatus": "ERROR",
                "mensaje": "El usuario no existe o no es un tutor",
                "status_code": 404
            }

        return self._actualizar_usuario_generico(id_usuario, datos_actualizacion, usuario_actual, "tutor")

    def actualizar_coordinador(self, id_usuario: str, datos_actualizacion: dict, usuario_actual: dict) -> dict:
        usuario = self.usuarios.find_one({"_id": ObjectId(id_usuario), "tipo": "coordinador"})
        if not usuario:
            return {
                "estatus": "ERROR",
                "mensaje": "El usuario no existe o no es un coordinador",
                "status_code": 404
            }

        return self._actualizar_usuario_generico(id_usuario, datos_actualizacion, usuario_actual, "coordinador")

    def _actualizar_usuario_generico(
            self,
            id_usuario: str,
            datos_actualizacion: dict,
            usuario_actual: dict,
            tipo_usuario: str
    ) -> dict:
        try:
            campos_validos = ["nombre", "apellidos", "email", "password", tipo_usuario]
            datos_set = {}

            for campo in campos_validos:
                if campo in datos_actualizacion:
                    if campo == "password":
                        hashed_password = bcrypt.hashpw(datos_actualizacion["password"].encode('utf-8'),
                                                        bcrypt.gensalt())
                        datos_set["password"] = hashed_password.decode('utf-8')
                    else:
                        datos_set[campo] = datos_actualizacion[campo]

            if not datos_set:
                return {
                    "estatus": "ERROR",
                    "mensaje": "No se proporcionaron datos válidos para actualizar",
                    "status_code": 400
                }

            self.usuarios.update_one({"_id": ObjectId(id_usuario)}, {"$set": datos_set})

            return {
                "estatus": "OK",
                "mensaje": "Usuario actualizado correctamente",
                "status_code": 200
            }

        except Exception as ex:
            print(f"Error al actualizar usuario {id_usuario}: {ex}")
            return {
                "estatus": "ERROR",
                "mensaje": "Error interno al actualizar el usuario",
                "status_code": 500
            }

    # Componente para la eliminación de usuarios

    def eliminar_usuario(self, id_usuario: str, no_empleado_coordinador: str) -> Dict[str, Any]:
        try:
            # 1. Validar ID de usuario
            if not ObjectId.is_valid(id_usuario):
                return {
                    "estatus": "ERROR",
                    "mensaje": "ID de usuario no válido",
                    "status_code": 400
                }

            # 2. Validar coordinador
            coordinador = self.usuarios.find_one({
                "coordinador.noEmpleado": no_empleado_coordinador,
                "tipo": "coordinador"
            })

            if not coordinador:
                return {
                    "estatus": "ERROR",
                    "mensaje": "Acceso denegado: Solo coordinadores pueden eliminar usuarios",
                    "status_code": 403
                }

            # 3. Obtener usuario completo antes de eliminar
            usuario = self.usuarios.find_one({"_id": ObjectId(id_usuario)})
            if not usuario:
                return {
                    "estatus": "ERROR",
                    "mensaje": "Usuario no encontrado",
                    "status_code": 404
                }

            # 4. Verificar dependencias
            if self.tiene_dependencias(id_usuario):
                return {
                    "estatus": "ERROR",
                    "mensaje": "El usuario tiene registros asociados y no puede ser eliminado",
                    "status_code": 409,
                    "usuario": self.formatear_usuario(usuario)  # Incluir datos aunque haya error
                }

            # 5. Eliminar y preparar respuesta
            self.usuarios.delete_one({"_id": ObjectId(id_usuario)})

            return {
                "estatus": "OK",
                "mensaje": "Usuario eliminado exitosamente",
                "status_code": 200,
                "usuario_eliminado": self.formatear_usuario(usuario),
                "no_empleado_coordinador": no_empleado_coordinador
            }

        except Exception as ex:
            print(f"Error al eliminar usuario: {ex}")
            return {
                "estatus": "ERROR",
                "mensaje": "Error interno del servidor",
                "status_code": 500
            }

    def tiene_dependencias(self, id_usuario: str) -> bool:
        """Verifica si el usuario tiene registros asociados"""
        return self.db.asistencias.count_documents({
            "$or": [
                {"id_alumno": ObjectId(id_usuario)},
                {"id_tutor": ObjectId(id_usuario)}
            ]
        }) > 0

    def formatear_usuario(self, usuario: Dict) -> Dict:
        """Aquí se formatea el documento de usuario para la respuesta"""
        usuario_formateado = {
            "id": str(usuario["_id"]),
            "email": usuario["email"],
            "nombre": usuario["nombre"],
            "apellidos": usuario["apellidos"],
            "tipo": usuario["tipo"],
            "fechaRegistro": usuario["fechaRegistro"]
        }

        if usuario["tipo"] == "alumno":
            usuario_formateado["alumno"] = usuario["alumno"]
        elif usuario["tipo"] == "tutor":
            usuario_formateado["tutor"] = usuario["tutor"]
        elif usuario["tipo"] == "coordinador":
            usuario_formateado["coordinador"] = usuario["coordinador"]

        return usuario_formateado
