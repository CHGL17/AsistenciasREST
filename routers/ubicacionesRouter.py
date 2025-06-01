from fastapi import APIRouter, Request, HTTPException
from models.ubicacionesModel import UbicacionInsert, UbicacionUpdate, Salida, UbicacionesSalida, UbicacionSelect, UbicacionSalida
from dao.ubicacionesDAO import UbicacionesDAO

router = APIRouter(
    prefix="/ubicaciones",
    tags=["Ubicaciones"]
)

@router.post("/", response_model=UbicacionSalida, summary="Crear una nueva ubicación")
async def crear_ubicacion(ubicacion: UbicacionInsert, request: Request) -> UbicacionSalida:
    ubicacionDAO = UbicacionesDAO(request.app.db)
    resultado = ubicacionDAO.crear_ubicacion(ubicacion)
    
    # Convertir el diccionario resultado a UbicacionSalida
    return UbicacionSalida(
        estatus=resultado["estatus"],
        mensaje=resultado["mensaje"],
        ubicacion=resultado["ubicacion"]
    )

@router.get("/", response_model=UbicacionesSalida, summary="Consultar todas las ubicaciones")
async def consultar_ubicaciones(request: Request) -> UbicacionesSalida:
    ubicacionDAO = UbicacionesDAO(request.app.db)
    return ubicacionDAO.obtener_ubicaciones()

@router.get("/{ubicacion_id}", response_model=UbicacionSalida, summary="Consultar una ubicación por su ID")
async def consultar_ubicacion_por_id(ubicacion_id: str, request: Request) -> UbicacionSalida:
    ubicacionDAO = UbicacionesDAO(request.app.db)
    return ubicacionDAO.obtener_ubicacion_por_id(ubicacion_id)

@router.put("/{ubicacion_id}", response_model=UbicacionSalida, summary="Actualizar una ubicación")
async def editar_ubicacion(ubicacion_id: str, ubicacion: UbicacionInsert, request: Request) -> UbicacionSalida:
    ubicacionDAO = UbicacionesDAO(request.app.db)
    return ubicacionDAO.editar_ubicacion(ubicacion_id, ubicacion)

@router.delete("/{ubicacion_id}", response_model=Salida, summary="Cancelar una ubicación")
async def cancelar_ubicacion(ubicacion_id: str, request: Request) -> Salida:
    ubicacionDAO = UbicacionesDAO(request.app.db)
    return ubicacionDAO.cancelar_ubicacion(ubicacion_id)