from fastapi import APIRouter, Request
from models.usuariosModel import (
    UsuarioAlumnoInsert,
    UsuarioTutorInsert,
    UsuarioCoordInsert,
    Salida
)
from dao.usuariosDAO import UsuarioDAO

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


@router.post("/publico", response_model=Salida, summary="Registro solo para alumnos (sin autenticación)")
async def registro_publico(usuario: UsuarioAlumnoInsert, request: Request) -> Salida:
    usuarioDAO = UsuarioDAO(request.app.db)
    return usuarioDAO.agregarUsuario(usuario)


@router.post("/privado/tutor", response_model=Salida, summary="Registro exclusivo para tutores")
async def registro_tutor(usuario: UsuarioTutorInsert, request: Request) -> Salida:
    usuarioDAO = UsuarioDAO(request.app.db)
    return usuarioDAO.agregarUsuario(usuario)


@router.post("/privado/coordinador", response_model=Salida, summary="Registro exclusivo para coordinadores")
async def registro_coordinador(usuario: UsuarioCoordInsert, request: Request) -> Salida:
    usuarioDAO = UsuarioDAO(request.app.db)
    return usuarioDAO.agregarUsuario(usuario)
