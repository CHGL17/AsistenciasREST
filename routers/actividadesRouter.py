from fastapi import APIRouter

router = APIRouter(prefix="/actividades", tags=["Actividades"])

@router.get("/")
async def listar_actividades():
    return {"mensaje": "Lista de actividades"}