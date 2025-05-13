from models.usuariosModel import (
    UsuarioAlumnoInsert,
    UsuarioTutorInsert,
    UsuarioCoordInsert,
    Salida
)
from fastapi.encoders import jsonable_encoder
import bcrypt
from typing import Union


class UsuarioDAO:
    def __init__(self, db):
        self.db = db

    def agregarUsuario(
        self,
        usuario: Union[UsuarioAlumnoInsert, UsuarioTutorInsert, UsuarioCoordInsert]
    ) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # Verificar que el email no exista ya
            if self.db.usuarios.find_one({"email": usuario.email}):
                return Salida(estatus="ERROR", mensaje="El correo ya está registrado.")

            # Hashear contraseña
            hashed_password = bcrypt.hashpw(usuario.password.encode('utf-8'), bcrypt.gensalt())

            # Convertir modelo a dict y asignar la contraseña hasheada
            usuario_dict = usuario.dict()
            usuario_dict["password"] = hashed_password.decode("utf-8")

            # Validaciones específicas por tipo
            if usuario.tipo == "alumno":
                # Validar solo tenga clave "alumno"
                if "alumno" not in usuario_dict or not usuario_dict["alumno"]:
                    return Salida(estatus="ERROR", mensaje="Datos del alumno requeridos.")
                if "tutor" in usuario_dict or "coordinador" in usuario_dict:
                    usuario_dict.pop("tutor", None)
                    usuario_dict.pop("coordinador", None)

            elif usuario.tipo == "tutor":
                if "tutor" not in usuario_dict or not usuario_dict["tutor"]:
                    return Salida(estatus="ERROR", mensaje="Datos del tutor requeridos.")
                if "alumno" in usuario_dict or "coordinador" in usuario_dict:
                    usuario_dict.pop("alumno", None)
                    usuario_dict.pop("coordinador", None)

            elif usuario.tipo == "coordinador":
                if "coordinador" not in usuario_dict or not usuario_dict["coordinador"]:
                    return Salida(estatus="ERROR", mensaje="Datos del coordinador requeridos.")
                if "alumno" in usuario_dict or "tutor" in usuario_dict:
                    usuario_dict.pop("alumno", None)
                    usuario_dict.pop("tutor", None)

            else:
                return Salida(estatus="ERROR", mensaje="Tipo de usuario no válido.")

            # Insertar a MongoDB
            result = self.db.usuarios.insert_one(jsonable_encoder(usuario_dict))
            return Salida(estatus="OK", mensaje="Usuario creado con id: " + str(result.inserted_id))

        except Exception as ex:
            print(f"Error interno al registrar usuario: {ex}")
            return Salida(estatus="ERROR", mensaje="Error interno al agregar usuario.")
