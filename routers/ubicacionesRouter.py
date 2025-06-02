from fastapi import APIRouter, Request, HTTPException, Depends
from models.ubicacionesModel import UbicacionInsert, UbicacionUpdate, Salida, UbicacionesSalida, UbicacionSelect, UbicacionSalida
from dao.ubicacionesDAO import UbicacionesDAO
from dao.auth import require_rol, require_roles

router = APIRouter(
    prefix="/ubicaciones",
    tags=["Ubicaciones"]
)

@router.post("/", response_model=UbicacionSalida, summary="Crear una nueva ubicación")
async def crear_ubicacion(
    ubicacion: UbicacionInsert, 
    request: Request,
    current_user: dict = Depends(require_rol("coordinador"))
) -> UbicacionSalida:
    """
    Crear una nueva ubicación - Solo Coordinadores
    """
    ubicacionDAO = UbicacionesDAO(request.app.db)
    resultado = ubicacionDAO.crear_ubicacion(ubicacion)
    
    # Convertir el diccionario resultado a UbicacionSalida
    return UbicacionSalida(
        estatus=resultado["estatus"],
        mensaje=resultado["mensaje"],
        ubicacion=resultado["ubicacion"]
    )

@router.get("/", response_model=UbicacionesSalida, summary="Consultar todas las ubicaciones")
async def consultar_ubicaciones(
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor"]))
) -> UbicacionesSalida:
    """
    Consultar todas las ubicaciones - Coordinadores y Tutores
    """
    ubicacionDAO = UbicacionesDAO(request.app.db)
    return ubicacionDAO.obtener_ubicaciones()

@router.get("/{ubicacion_id}", response_model=UbicacionSalida, summary="Consultar una ubicación por su ID")
async def consultar_ubicacion_por_id(
    ubicacion_id: str, 
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor"]))
) -> UbicacionSalida:
    """
    Consultar una ubicación específica - Coordinadores y Tutores
    """
    ubicacionDAO = UbicacionesDAO(request.app.db)
    return ubicacionDAO.obtener_ubicacion_por_id(ubicacion_id)

@router.put("/{ubicacion_id}", response_model=UbicacionSalida, summary="Actualizar una ubicación")
async def editar_ubicacion(
    ubicacion_id: str, 
    ubicacion: UbicacionInsert, 
    request: Request,
    current_user: dict = Depends(require_rol("coordinador"))
) -> UbicacionSalida:
    """
    Actualizar una ubicación - Solo Coordinadores
    """
    ubicacionDAO = UbicacionesDAO(request.app.db)
    return ubicacionDAO.editar_ubicacion(ubicacion_id, ubicacion)

@router.delete("/{ubicacion_id}", response_model=Salida, summary="Cancelar una ubicación")
async def cancelar_ubicacion(
    ubicacion_id: str, 
    request: Request,
    current_user: dict = Depends(require_rol("coordinador"))
) -> Salida:
    """
    Cancelar una ubicación - Solo Coordinadores
    """
    ubicacionDAO = UbicacionesDAO(request.app.db)
    return ubicacionDAO.cancelar_ubicacion(ubicacion_id)