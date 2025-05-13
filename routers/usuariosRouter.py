from fastapi import APIRouter, Request
from models.usuariosModel import UsuarioInsert, Salida
from dao.usuariosDAO import UsuarioDAO

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)

@router.post("/", response_model=Salida)
async def crearUsuario(usuario: UsuarioInsert, request: Request) -> Salida:
    usuarioDAO = UsuarioDAO(request.app.db)
    return usuarioDAO.agregarUsuario(usuario)
