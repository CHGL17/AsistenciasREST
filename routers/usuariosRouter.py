from fastapi import APIRouter, Request, HTTPException
from models.usuariosModel import UsuarioInsert, Salida
from dao.usuariosDAO import UsuarioDAO

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


@router.post("/publico", response_model=Salida, summary="Registro solo para alumnos (sin autenticación)")
async def registro_publico(usuario: UsuarioInsert, request: Request) -> Salida:
    if usuario.tipo != "alumno":
        raise HTTPException(status_code=403, detail="Sólo se permite registrar alumnos en esta ruta.")

    usuarioDAO = UsuarioDAO(request.app.db)
    return usuarioDAO.agregarUsuario(usuario)

@router.post("/privado", response_model=Salida, summary="Registro para coordinadores (crear tutor o coordinador)")
async def registro_privado(usuario: UsuarioInsert, request: Request) -> Salida:
    if usuario.tipo not in ["tutor", "coordinador"]:
        raise HTTPException(status_code=403, detail="Esta ruta es sólo para crear tutores o coordinadores.")

    usuarioDAO = UsuarioDAO(request.app.db)
    return usuarioDAO.agregarUsuario(usuario)