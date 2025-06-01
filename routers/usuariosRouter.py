# Importación de librerías, modelos, dao, etc.
from fastapi import APIRouter, Request, HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.usuariosModel import (
    UsuarioAlumnoInsert, UsuarioTutorInsert, UsuarioCoordInsert, Salida,
    UsuarioSalidaID, UsuarioSalidaLista, UsuarioEliminadoResponse
    # , ActualizarTutorRequest,
    # ActualizarCoordinadorRequest, ActualizarAlumnoRequest
)
from dao.usuariosDAO import UsuarioDAO
from typing import Annotated

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
def get_usuario_dao(request: Request) -> UsuarioDAO:
    return UsuarioDAO(request.app.db)


# Función simulada de autenticación (TEMPORAL - para desarrollo)
def get_current_user():
    return {"tipo": "coordinador"}  # Simulado, en producción usar JWT o sesión


# ============ ENDPOINTS ============ #

# Registro público para alumnos
@router.post("/publico/alumno", response_model=Salida, status_code=status.HTTP_201_CREATED,
             summary="Registro público para alumnos", response_description="Resultado del registro")
def registro_publico(usuario: UsuarioAlumnoInsert, usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)]):
    resultado = usuario_dao.agregarUsuario(usuario)
    if resultado.estatus == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado.mensaje
        )
    return resultado


# Registro para tutores (requiere autenticación)
@router.post("/privado/tutor", response_model=Salida, status_code=status.HTTP_201_CREATED,
             summary="Registro para tutores", response_description="Resultado del registro")
def registro_tutor(usuario: UsuarioTutorInsert, usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)]):
    resultado = usuario_dao.agregarUsuario(usuario)
    if resultado.estatus == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado.mensaje
        )
    return resultado


# Registro para coordinadores (requiere autenticación)
@router.post("/privado/coordinador", response_model=Salida, status_code=status.HTTP_201_CREATED,
             summary="Registro para coordinadores", response_description="Resultado del registro")
def registro_coordinador(usuario: UsuarioCoordInsert, usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)]):
    resultado = usuario_dao.agregarUsuario(usuario)
    if resultado.estatus == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado.mensaje
        )
    return resultado


# Consultar usuario por ID
@router.get("/{id_usuario}", response_model=UsuarioSalidaID, summary="Consultar un usuario por su ID",
            responses={
                404: {"model": UsuarioSalidaID, "description": "Usuario no encontrado"},
                500: {"model": UsuarioSalidaID, "description": "Error interno del servidor"}
            })
def consultar_usuario_por_id(
        id_usuario: str,
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)]
):
    resultado = usuario_dao.consultarUsuarioPorID(id_usuario)
    if resultado.estatus == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "no encontrado" in resultado.mensaje else status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=resultado.mensaje
        )
    return resultado


# Consulta general de usuarios
@router.get("/general/", response_model=UsuarioSalidaLista, summary="Consulta general de usuarios",
            response_description="Lista completa de usuarios registrados")
def consulta_general_usuarios(usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)]):
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
        current_user: dict = Depends(get_current_user)
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
    "/{id_usuario}",
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
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)]
):
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
        coordinador_autorizador="(pendiente_autenticacion_jwt)"
    )
