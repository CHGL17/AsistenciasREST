

from fastapi import APIRouter, Request, HTTPException, Depends # Asegúrate de que Depends esté importado
from models.carrerasModel import CarreraInsert, CarreraUpdate, CarreraSalida, CarrerasSalida
from dao.carrerasDao import CarreraDAO
from dao.auth import require_rol, require_roles # Importa tus funciones de autenticación/autorización

router = APIRouter(
    prefix="/carreras",
    tags=["Carreras"]
)

@router.post("/", response_model=CarreraSalida, status_code=201, summary="Crear una nueva carrera")
async def crear_carrera(
    carrera: CarreraInsert,
    request: Request,
    current_user: dict = Depends(require_rol("coordinador")) # Solo Coordinador
) -> CarreraSalida:
    """
    Crea una nueva carrera.
    - **Permitido para:** Coordinador
    """
    carrera_dao = CarreraDAO(request.app.db)
    return await carrera_dao.agregar_carrera(carrera)

@router.get("/", response_model=CarrerasSalida, summary="Consultar todas las carreras")
async def consultar_carreras(
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor", "estudiante"])) # Coordinador, Tutor, Estudiante
) -> CarrerasSalida:
    """
    Obtiene la lista de todas las carreras.
    - **Permitido para:** Coordinador, Tutor, Estudiante
    """
    carrera_dao = CarreraDAO(request.app.db)
    return await carrera_dao.consulta_general_carreras()

@router.get("/{carrera_id}", response_model=CarreraSalida, summary="Consultar una carrera por su ID")
async def consultar_carrera_por_id(
    carrera_id: int, # Asumiendo que carrera_id es un entero según el código original
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor", "estudiante"])) # Coordinador, Tutor, Estudiante
) -> CarreraSalida:
    """
    Obtiene una carrera específica por su ID.
    - **Permitido para:** Coordinador, Tutor, Estudiante
    """
    carrera_dao = CarreraDAO(request.app.db)
    return await carrera_dao.consultar_carrera_por_id(carrera_id)

@router.put("/{carrera_id}", response_model=CarreraSalida, summary="Actualizar una carrera")
async def actualizar_carrera(
    carrera_id: int, # Asumiendo que carrera_id es un entero
    carrera: CarreraUpdate,
    request: Request,
    current_user: dict = Depends(require_rol("coordinador")) # Solo Coordinador
) -> CarreraSalida:
    """
    Actualiza la información de una carrera existente.
    - **Permitido para:** Coordinador
    """
    carrera_dao = CarreraDAO(request.app.db)
    return await carrera_dao.actualizar_carrera(carrera_id, carrera)

@router.delete("/{carrera_id}", response_model=CarreraSalida, summary="Eliminar una carrera") # La imagen dice "Cancelar"
async def eliminar_carrera(
    carrera_id: int, # Asumiendo que carrera_id es un entero
    request: Request,
    current_user: dict = Depends(require_rol("coordinador")) # Solo Coordinador
) -> CarreraSalida:
    """
    Elimina una carrera. (La imagen lo refiere como "Cancelar carrera")
    - **Permitido para:** Coordinador
    """
    carrera_dao = CarreraDAO(request.app.db)
    return await carrera_dao.eliminar_carrera(carrera_id)

