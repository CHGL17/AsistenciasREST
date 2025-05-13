# Importación de librerías, modelos, dao, etc.
from fastapi import APIRouter, Request, HTTPException, status, Depends
from models.usuariosModel import UsuarioAlumnoInsert, UsuarioTutorInsert, UsuarioCoordInsert, Salida, UsuarioSalidaID, AlumnoResponse, TutorResponse, CoordinadorResponse
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

@router.get("/{id_usuario}",response_model=UsuarioSalidaID,summary="Consultar un usuario por su ID",
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
