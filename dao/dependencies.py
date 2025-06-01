from fastapi import Request
from dao.usuariosDAO import UsuarioDAO

def get_usuario_dao(request: Request) -> UsuarioDAO:
    return UsuarioDAO(request.app.db)
