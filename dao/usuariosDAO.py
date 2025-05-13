from models.usuariosModel import UsuarioAlumnoInsert,UsuarioTutorInsert,UsuarioCoordInsert,Salida
from fastapi.encoders import jsonable_encoder
import bcrypt
import re
from datetime import datetime
from typing import Union
from pymongo import MongoClient


class UsuarioDAO:
    def __init__(self, db: MongoClient):
        self.db = db
        self.usuarios = db.usuarios
        self.carreras = db.carreras
#Valicación de campos y parámetros generales
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
