

from fastapi import APIRouter, Request, HTTPException, Depends # Asegúrate de que Depends esté importado
from models.ciclosModel import CicloInsert, CicloUpdate, CicloSalida, CiclosSalida, Salida
from dao.ciclosDAO import CicloDAO
from dao.auth import require_rol, require_roles # Importa tus funciones de autenticación/autorización
from typing import List

router = APIRouter(
    prefix="/ciclos",
    tags=["Ciclos"]
)

@router.post("/", response_model=CicloSalida, status_code=201, summary="Crear un nuevo ciclo")
async def crearCiclo(
    ciclo: CicloInsert,
    request: Request,
    current_user: dict = Depends(require_rol("coordinador")) # Solo Coordinador
) -> CicloSalida:
    """
    Crea un nuevo ciclo académico.
    - **Permitido para:** Coordinador
    """
    ciclo_dao = CicloDAO(request.app.db)
    return await ciclo_dao.agregar(ciclo)

@router.get("/", response_model=CiclosSalida, summary="Consultar todos los ciclos")
async def consultarCiclos(
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor", "estudiante"])) # Coordinador, Tutor, Estudiante
) -> CiclosSalida:
    """
    Obtiene la lista de todos los ciclos académicos.
    - **Permitido para:** Coordinador, Tutor, Estudiante
    """
    ciclo_dao = CicloDAO(request.app.db)
    return await ciclo_dao.consultaGeneral()

@router.get("/{idCiclo}", response_model=CicloSalida, summary="Consultar un ciclo por su ID")
async def consultarCicloPorID(
    idCiclo: str,
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor", "estudiante"])) # Coordinador, Tutor, Estudiante
) -> CicloSalida:
    """
    Obtiene un ciclo académico específico por su ID.
    - **Permitido para:** Coordinador, Tutor, Estudiante
    """
    ciclo_dao = CicloDAO(request.app.db)
    return await ciclo_dao.consultarPorID(idCiclo)

@router.put("/{idCiclo}", response_model=CicloSalida, summary="Actualizar un ciclo")
async def actualizarCiclo(
    idCiclo: str,
    ciclo: CicloUpdate,
    request: Request,
    current_user: dict = Depends(require_rol("coordinador")) # Solo Coordinador
) -> CicloSalida:
    """
    Actualiza la información de un ciclo académico existente.
    - **Permitido para:** Coordinador
    """
    ciclo_dao = CicloDAO(request.app.db)
    return await ciclo_dao.actualizar(idCiclo, ciclo)

@router.delete("/{idCiclo}", response_model=Salida, summary="Eliminar un ciclo")
async def eliminarCiclo( # La imagen dice "Cancelar", pero la función se llama "eliminar"
    idCiclo: str,
    request: Request,
    current_user: dict = Depends(require_rol("coordinador")) # Solo Coordinador
) -> Salida:
    """
    Elimina un ciclo académico. (La imagen lo refiere como "Cancelar ciclo")
    - **Permitido para:** Coordinador
    """
    ciclo_dao = CicloDAO(request.app.db)
    return await ciclo_dao.eliminar(idCiclo)

