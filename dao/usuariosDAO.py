from models.usuariosModel import UsuarioInsert, Salida
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
import bcrypt

class UsuarioDAO:
    def __init__(self, db):
        self.db = db

    def agregarUsuario(self, usuario: UsuarioInsert) -> Salida:
        salida = Salida(estatus="", mensaje="")
        try:
            # Validar email único
            existe = self.db.usuarios.find_one({"email": usuario.email})
            if existe:
                salida.estatus = "ERROR"
                salida.mensaje = "El correo ya está registrado."
                return salida

            # Validar tipo y datos requeridos
            if usuario.tipo == "alumno":
                if not usuario.alumno:
                    salida.estatus = "ERROR"
                    salida.mensaje = "Datos de alumno requeridos."
                    return salida
            elif usuario.tipo == "tutor":
                if not usuario.tutor:
                    salida.estatus = "ERROR"
                    salida.mensaje = "Datos de tutor requeridos."
                    return salida
            elif usuario.tipo == "coordinador":
                if not usuario.coordinador:
                    salida.estatus = "ERROR"
                    salida.mensaje = "Datos de coordinador requeridos."
                    return salida
            else:
                salida.estatus = "ERROR"
                salida.mensaje = "Tipo de usuario no válido."
                return salida

            # Hashear contraseña
            hashed_password = bcrypt.hashpw(usuario.password.encode('utf-8'), bcrypt.gensalt())

            # Exportar sólo campos que no sean None (limpio)
            usuario_dict = usuario.dict(exclude_none=True)
            usuario_dict["password"] = hashed_password.decode('utf-8')

            # Insertar en Mongo
            result = self.db.usuarios.insert_one(jsonable_encoder(usuario_dict))

            salida.estatus = "OK"
            salida.mensaje = "Usuario creado con id: " + str(result.inserted_id)

        except Exception as ex:
            print(f"Error al crear usuario: {ex}")
            salida.estatus = "ERROR"
            salida.mensaje = "Error interno al agregar usuario."

        return salida
