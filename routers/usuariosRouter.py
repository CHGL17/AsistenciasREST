# Importación de librerías, modelos, dao, etc.
from fastapi import APIRouter, Request, HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.usuariosModel import (
    UsuarioAlumnoInsert, UsuarioTutorInsert, UsuarioCoordInsert, Salida,
    UsuarioSalidaID, UsuarioSalidaLista, UsuarioEliminadoResponse
    # , ActualizarTutorRequest,
    # ActualizarCoordinadorRequest, ActualizarAlumnoRequest
)
from dao.dependencies import get_usuario_dao
from dao.auth import create_access_token, require_coordinador, require_roles, require_rol
from dao.usuariosDAO import UsuarioDAO
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
import bcrypt
from dao.database import Conexion

# Configuración básica del router
router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    responses={
        400: {"model": Salida, "description": "Datos de entrada inválidos"},
        500: {"model": Salida, "description": "Error interno del servidor"}
    }
)

# Configuración de seguridad
security = HTTPBearer()


# Función para obtener el DAO


# Función simulada de autenticación (TEMPORAL - para desarrollo)
def get_current_user():
    return {"tipo": "coordinador"}  # Simulado, en producción usar JWT o sesión


# ============ ENDPOINTS ============ #

# LogIn
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = Conexion().getDB()
    user = db["usuarios"].find_one({"email": form_data.username})

    if not user or not bcrypt.checkpw(form_data.password.encode("utf-8"), user["password"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if user["status"] != "activo":
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    token = create_access_token(data={"user_id": str(user["_id"]), "tipo": user["tipo"]})
    return {"access_token": token, "token_type": "bearer"}


# Registro público para alumnos
@router.post(
    "/privado/alumno",
    response_model=Salida,
    status_code=status.HTTP_201_CREATED,
    summary="Registro privado para alumnos",
    response_description="Resultado del registro"
)
def registro_alumno(
        usuario: UsuarioAlumnoInsert,
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
        current_user: dict = Depends(require_roles(["alumno", "coordinador"]))  # 🔒 solo alumnos y coordinadores
):
    resultado = usuario_dao.agregarUsuario(usuario)
    if resultado.estatus == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado.mensaje
        )
    return resultado


# Registro para tutores (requiere autenticación)
@router.post(
    "/privado/tutor",
    response_model=Salida,
    status_code=status.HTTP_201_CREATED,
    summary="Registro para tutores",
    response_description="Resultado del registro"
)
def registro_tutor(
        usuario: UsuarioTutorInsert,
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
        current_user: dict = Depends(require_roles(["tutor", "coordinador"]))  # ✅ permite ambos
):
    resultado = usuario_dao.agregarUsuario(usuario)
    if resultado.estatus == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado.mensaje
        )
    return resultado


# Registro para coordinadores (requiere autenticación)
@router.post(
    "/privado/coordinador",
    response_model=Salida,
    status_code=status.HTTP_201_CREATED,
    summary="Registro para coordinadores",
    response_description="Resultado del registro"
)
def registro_coordinador(
        usuario: UsuarioCoordInsert,
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
        current_user: dict = Depends(require_rol("coordinador"))  # 🔒 sólo coordinadores
):
    resultado = usuario_dao.agregarUsuario(usuario)
    if resultado.estatus == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado.mensaje
        )
    return resultado


# Consultar usuario por ID
from dao.auth import get_current_user, validar_acceso_consulta


@router.get("/{id_usuario}", response_model=UsuarioSalidaID, summary="Consultar un usuario por su ID",
            responses={
                403: {"description": "Acceso denegado"},
                404: {"model": UsuarioSalidaID, "description": "Usuario no encontrado"},
                500: {"model": UsuarioSalidaID, "description": "Error interno del servidor"}
            })
def consultar_usuario_por_id(
        id_usuario: str,
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
        current_user: dict = Depends(get_current_user)
):
    resultado = usuario_dao.consultarUsuarioPorID(id_usuario)

    if resultado.estatus == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "no encontrado" in resultado.mensaje else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=resultado.mensaje
        )

    tipo_objetivo = resultado.usuario.tipo  # ✅ Corregido

    validar_acceso_consulta(current_user, tipo_objetivo, id_usuario)

    return resultado


# Consulta general de usuarios
@router.get("/general/", response_model=UsuarioSalidaLista, summary="Consulta general de usuarios",
            response_description="Lista completa de usuarios registrados",
            responses={
                403: {"description": "Solo accesible para coordinadores"}
            })
def consulta_general_usuarios(
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
        current_user: dict = Depends(require_rol("coordinador"))  # 🔐 solo coordinadores
):
    return usuario_dao.consultaGeneralUsuarios()


# === ACTUALIZAR ALUMNO ===
@router.put("/alumno/{id_usuario}", response_model=Salida)
def actualizar_alumno(
        id_usuario: str,
        datos: UsuarioAlumnoInsert,  # Se usa el mismo modelo de registro
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
        current_user: dict = Depends(get_current_user)
):
    datos_dict = datos.model_dump(exclude_unset=True)
    resultado = usuario_dao.actualizar_alumno(id_usuario, datos_dict, current_user)

    if resultado["estatus"] == "ERROR":
        raise HTTPException(status_code=resultado["status_code"], detail=resultado["mensaje"])
    return Salida(estatus="OK", mensaje="Alumno actualizado correctamente.")


# === ACTUALIZAR TUTOR ===
@router.put("/tutor/{id_usuario}", response_model=Salida)
def actualizar_tutor(
        id_usuario: str,
        datos: UsuarioTutorInsert,
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
        current_user: dict = Depends(lambda: require_self_or_coordinador(id_usuario))
):
    datos_dict = datos.model_dump(exclude_unset=True)
    resultado = usuario_dao.actualizar_tutor(id_usuario, datos_dict, current_user)

    if resultado["estatus"] == "ERROR":
        raise HTTPException(status_code=resultado["status_code"], detail=resultado["mensaje"])
    return Salida(estatus="OK", mensaje="Tutor actualizado correctamente.")


# === ACTUALIZAR COORDINADOR ===
@router.put("/coordinador/{id_usuario}", response_model=Salida)
def actualizar_coordinador(
        id_usuario: str,
        datos: UsuarioCoordInsert,
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
        current_user: dict = Depends(get_current_user)
):
    datos_dict = datos.model_dump(exclude_unset=True)
    resultado = usuario_dao.actualizar_coordinador(id_usuario, datos_dict, current_user)

    if resultado["estatus"] == "ERROR":
        raise HTTPException(status_code=resultado["status_code"], detail=resultado["mensaje"])
    return Salida(estatus="OK", mensaje="Coordinador actualizado correctamente.")


# Eliminar usuario
@router.delete(
    "/usuarios/{id_usuario}",
    response_model=UsuarioEliminadoResponse,
    summary="Eliminar lógicamente un usuario (cambia status a inactivo)",
    responses={
        200: {"description": "Usuario desactivado con éxito"},
        400: {"description": "ID inválido"},
        404: {"description": "Usuario no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
def eliminar_usuario_logico(
        id_usuario: str,
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
        current_user: dict = Depends(require_coordinador)
):
    try:
        resultado = usuario_dao.eliminar_usuario_logico(id_usuario)

        if resultado["estatus"] == "ERROR":
            raise HTTPException(
                status_code=resultado["status_code"],
                detail=resultado["mensaje"]
            )

        return UsuarioEliminadoResponse(
            mensaje=resultado["mensaje"],
            detalles_eliminacion={
                "usuario": resultado["usuario_eliminado"],
                "operacion": "eliminacion_logica"
            },
            coordinador_autorizador=current_user["nombre"] + " " + current_user["apellidos"]
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="ID de usuario inválido")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno del servidor")
