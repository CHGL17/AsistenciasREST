from fastapi import APIRouter, Request, HTTPException
from models.actividadesModel import ActividadInsert, Salida, ActividadesSalida, ActividadSelectID, ActividadesSalidaID
from dao.actividadesDAO import ActividadDAO
router = APIRouter(
    prefix="/actividades",
    tags=["Actividades"]
)

#@router.post("/", response_model=Salida, summary="Crear una nueva actividad")
#async def crearActividad(actividad: ActividadInsert, request: Request) -> Salida:
#    actividadDAO = ActividadDAO(request.app.db)
#    usuario_actual = request.state.usuario
#    return await actividadDAO.agregar(actividad, usuario_actual)

@router.post("/", response_model=Salida, summary="Crear una nueva actividad")
async def crearActividad(actividad: ActividadInsert, request: Request) -> Salida:
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.agregar(actividad)

@router.get("/", response_model=ActividadesSalida, summary="Consultar todas las actividades")
async def consultaActividades(request : Request)->ActividadesSalida:
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.consultaGeneral()

@router.get("/{idActividad}", response_model=ActividadesSalidaID, summary="Consultar una actividad por su ID")
async def consultarActividadID(idActividad: str, request: Request) -> ActividadesSalidaID:
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.consultarActividadPorID(idActividad)

@router.put("/{idActividad}", response_model=ActividadesSalidaID, summary="Actualizar una actividad")
async def actualizarActividad(idActividad: str, actividad: ActividadInsert, request: Request) -> ActividadesSalidaID:
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.actualizar(idActividad, actividad)

@router.delete("/{idActividad}", response_model=Salida, summary="Eliminar una actividad")
async def eliminarActividad(idActividad: str, request: Request) -> Salida:
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.eliminar(idActividad)