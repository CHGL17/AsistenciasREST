# dao/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from bson import ObjectId
from dao.database import Conexion
import bcrypt
import os

# Configuración secreta
SECRET_KEY = "asistencias_secret_jwt"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/login")

# Generar token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Obtener usuario desde token
def get_current_user(token: str = Depends(oauth2_scheme)):
    from dao.database import Conexion
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    conexion = Conexion()
    user = conexion.getDB()["usuarios"].find_one({"_id": ObjectId(user_id), "status": "activo"})
    if not user:
        raise credentials_exception
    return user

# Validación de acceso a rutas explícitas de registro de usuarios Alumno-Tutor-Coordinador (útil para varios roles)

def require_roles(roles_permitidos: list[str]):
    def _verifica_roles(current_user: dict = Depends(get_current_user)):
        if current_user["tipo"] not in roles_permitidos:
            raise HTTPException(
                status_code=403,
                detail=f"Acceso solo permitido a usuarios tipo: {', '.join(roles_permitidos)}"
            )
        return current_user
    return _verifica_roles

# Exclusivo al coordinador
def require_rol(rol_requerido: str):
    def _verifica_rol(current_user: dict = Depends(get_current_user)):
        if current_user["tipo"] != rol_requerido:
            raise HTTPException(status_code=403, detail=f"Acceso solo permitido a usuarios tipo '{rol_requerido}'")
        return current_user
    return _verifica_rol

# dao/auth.py (Usuarios-Tutor)
def require_self_or_coordinador(id_objetivo: str, current_user: dict = Depends(get_current_user)):
    if current_user["tipo"] == "coordinador":
        return current_user
    if str(current_user["_id"]) != id_objetivo:
        raise HTTPException(status_code=403, detail="Solo puedes acceder o modificar tu propia cuenta")
    return current_user

# Verificar si es coordinador
def require_coordinador(current_user: dict = Depends(get_current_user)):
    if current_user["tipo"] != "coordinador":
        raise HTTPException(status_code=403, detail="Acceso solo permitido a coordinadores")
    return current_user