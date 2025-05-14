from fastapi import APIRouter, Request, HTTPException
from models.ciclosModel import CicloInsert, CicloUpdate, CicloSalida, CiclosSalida, Salida
from dao.ciclosDAO import CicloDAO
from typing import List

router = APIRouter(
    prefix="/ciclos",
    tags=["Ciclos"]
)

@router.post("/", response_model=CicloSalida, status_code=201, summary="Crear un nuevo ciclo")
async def crearCiclo(ciclo: CicloInsert, request: Request) -> CicloSalida:
    """
    Crea un nuevo ciclo académico.
    """
    ciclo_dao = CicloDAO(request.app.db)
    return await ciclo_dao.agregar(ciclo)

@router.get("/", response_model=CiclosSalida, summary="Consultar todos los ciclos")
async def consultarCiclos(request: Request) -> CiclosSalida:
    """
    Obtiene la lista de todos los ciclos académicos.
    """
    ciclo_dao = CicloDAO(request.app.db)
    return await ciclo_dao.consultaGeneral()

@router.get("/{idCiclo}", response_model=CicloSalida, summary="Consultar un ciclo por su ID")
async def consultarCicloPorID(idCiclo: str, request: Request) -> CicloSalida:
    """
    Obtiene un ciclo académico específico por su ID.
    """
    ciclo_dao = CicloDAO(request.app.db)
    return await ciclo_dao.consultarPorID(idCiclo)

@router.put("/{idCiclo}", response_model=CicloSalida, summary="Actualizar un ciclo")
async def actualizarCiclo(idCiclo: str, ciclo: CicloUpdate, request: Request) -> CicloSalida:
    """
    Actualiza la información de un ciclo académico existente.
    """
    ciclo_dao = CicloDAO(request.app.db)
    return await ciclo_dao.actualizar(idCiclo, ciclo)

@router.delete("/{idCiclo}", response_model=Salida, summary="Eliminar un ciclo")
async def eliminarCiclo(idCiclo: str, request: Request) -> Salida:
    """
    Elimina un ciclo académico.
    """
    ciclo_dao = CicloDAO(request.app.db)
    return await ciclo_dao.eliminar(idCiclo)