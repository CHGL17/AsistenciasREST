# Importación de librerías, modelos, dao, etc.
from fastapi import APIRouter, Request, HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.usuariosModel import (
    UsuarioAlumnoInsert, UsuarioTutorInsert, UsuarioCoordInsert, Salida,
    UsuarioSalidaID, UsuarioSalidaLista, EliminarUsuarioRequest,
    UsuarioEliminadoResponse, ActualizarTutorRequest,
    ActualizarCoordinadorRequest, ActualizarAlumnoRequest
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


# Actualizar usuario

@router.put(
    "/alumno/{id_usuario}",
    response_model=Salida,
    summary="Actualizar información de un alumno",
    responses={
        200: {"description": "Alumno actualizado exitosamente"},
        400: {"description": "Datos inválidos o sin cambios"},
        403: {"description": "No autorizado"},
        404: {"description": "Alumno no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def actualizar_alumno(
    id_usuario: str,
    datos_actualizacion: ActualizarAlumnoRequest,
    usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
    current_user: dict = Depends(get_current_user)
):
    datos_dict = datos_actualizacion.model_dump(exclude_unset=True)
    resultado = usuario_dao.actualizar_alumno(id_usuario, datos_dict, current_user)

    if resultado["estatus"] == "ERROR":
        raise HTTPException(status_code=resultado["status_code"], detail=resultado["mensaje"])

    return Salida(estatus="OK", mensaje="Alumno actualizado correctamente.")


# Actualizar TUTOR
@router.put(
    "/tutor/{id_usuario}",
    response_model=Salida,
    summary="Actualizar información de un tutor",
    responses={
        200: {"description": "Tutor actualizado exitosamente"},
        400: {"description": "Datos inválidos o sin cambios"},
        403: {"description": "No autorizado"},
        404: {"description": "Tutor no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def actualizar_tutor(
    id_usuario: str,
    datos_actualizacion: ActualizarTutorRequest,
    usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
    current_user: dict = Depends(get_current_user)
):
    datos_dict = datos_actualizacion.model_dump(exclude_unset=True)
    resultado = usuario_dao.actualizar_tutor(id_usuario, datos_dict, current_user)

    if resultado["estatus"] == "ERROR":
        raise HTTPException(status_code=resultado["status_code"], detail=resultado["mensaje"])

    return Salida(estatus="OK", mensaje="Tutor actualizado correctamente.")


# Actualizar COORDINADOR
@router.put(
    "/coordinador/{id_usuario}",
    response_model=Salida,
    summary="Actualizar información de un coordinador",
    responses={
        200: {"description": "Coordinador actualizado exitosamente"},
        400: {"description": "Datos inválidos o sin cambios"},
        403: {"description": "No autorizado"},
        404: {"description": "Coordinador no encontrado"},
        500: {"description": "Error interno del servidor"}
    }
)
async def actualizar_coordinador(
    id_usuario: str,
    datos_actualizacion: ActualizarCoordinadorRequest,
    usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)],
    current_user: dict = Depends(get_current_user)
):
    datos_dict = datos_actualizacion.model_dump(exclude_unset=True)
    resultado = usuario_dao.actualizar_coordinador(id_usuario, datos_dict, current_user)

    if resultado["estatus"] == "ERROR":
        raise HTTPException(status_code=resultado["status_code"], detail=resultado["mensaje"])

    return Salida(estatus="OK", mensaje="Coordinador actualizado correctamente.")
# Eliminar usuario
@router.delete(
    "/{id_usuario}",
    response_model=UsuarioEliminadoResponse,
    summary="Eliminar un usuario permanentemente",
    responses={
        200: {"description": "Usuario eliminado con éxito"},
        400: {"description": "ID inválido"},
        403: {"description": "No autorizado"},
        404: {"description": "Usuario no encontrado"},
        409: {"description": "El usuario tiene dependencias"},
        500: {"description": "Error interno del servidor"}
    }
)
def eliminar_usuario(
        id_usuario: str,
        datos_autorizacion: EliminarUsuarioRequest,
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)]
):
    resultado = usuario_dao.eliminar_usuario(
        id_usuario=id_usuario,
        no_empleado_coordinador=datos_autorizacion.no_empleado_coordinador
    )

    if resultado["estatus"] == "ERROR":
        if resultado.get("usuario"):
            raise HTTPException(
                status_code=resultado["status_code"],
                detail={
                    "mensaje": resultado["mensaje"],
                    "usuario": resultado["usuario"]
                }
            )
        raise HTTPException(
            status_code=resultado["status_code"],
            detail=resultado["mensaje"]
        )

    return UsuarioEliminadoResponse(
        mensaje=resultado["mensaje"],
        detalles_eliminacion={
            "usuario": resultado["usuario_eliminado"],
            "operacion": "eliminacion_permanente"
        },
        coordinador_autorizador=resultado["no_empleado_coordinador"]
    )