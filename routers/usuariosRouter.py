# Importación de librerías, modelos, dao, etc.
from fastapi import APIRouter, Request, HTTPException, status, Depends
from models.usuariosModel import UsuarioAlumnoInsert, UsuarioTutorInsert, UsuarioCoordInsert, Salida, UsuarioSalidaID, \
    UsuarioSalidaLista, \
    EliminarUsuarioRequest, UsuarioEliminadoResponse
from dao.usuariosDAO import UsuarioDAO
from typing import Annotated

# Ruta del servicio
router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    responses={
        400: {"model": Salida, "description": "Datos de entrada inválidos"},
        500: {"model": Salida, "description": "Error interno del servidor"}
    }
)


def get_usuario_dao(request: Request) -> UsuarioDAO:
    return UsuarioDAO(request.app.db)


# Definición de métodos enrutados en el servicio que usamos para el registro de usuarios

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


@router.post("/privado/tutor", response_model=Salida, status_code=status.HTTP_201_CREATED,
             summary="Registro para tutores (requiere autenticación)", response_description="Resultado del registro")
def registro_tutor(usuario: UsuarioTutorInsert, usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)]):
    resultado = usuario_dao.agregarUsuario(usuario)
    if resultado.estatus == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado.mensaje
        )
    return resultado


@router.post("/privado/coordinador", response_model=Salida, status_code=status.HTTP_201_CREATED,
             summary="Registro para coordinadores (requiere autenticación)",
             response_description="Resultado del registro")
def registro_coordinador(usuario: UsuarioCoordInsert, usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)]):
    resultado = usuario_dao.agregarUsuario(usuario)
    if resultado.estatus == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=resultado.mensaje
        )
    return resultado


# Definición de rutas para la consulta por ID de usuarios

@router.get("/{id_usuario}", response_model=UsuarioSalidaID, summary="Consultar un usuario por su ID",
            responses={
                404: {"model": UsuarioSalidaID, "description": "Usuario no encontrado"},
                500: {"model": UsuarioSalidaID, "description": "Error interno del servidor"}
            }
            )
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


# Definición de rutas para la consulta general de usuarios

@router.get("/general/",
            response_model=UsuarioSalidaLista,
            summary="Consulta general de usuarios",
            response_description="Lista completa de usuarios registrados")
def consulta_general_usuarios(
        usuario_dao: Annotated[UsuarioDAO, Depends(get_usuario_dao)]
):
    return usuario_dao.consultaGeneralUsuarios()


# Definición de la ruta y parámetros para la elimnación de usuarios

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
from datetime import datetime

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
        # Incluir detalles del usuario en errores 409
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