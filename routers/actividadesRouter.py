from fastapi import APIRouter, Request, HTTPException
from models.usuariosModel import UsuarioInsert
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
    try:
        usuario_actual = request.state.usuario
    except AttributeError:
        raise HTTPException(
            status_code=401,
            detail="Se requiere autenticación para crear actividades"
        )
    return await actividadDAO.agregar(actividad, usuario_actual)

@router.get("/", response_model=ActividadesSalida, summary="Consultar todas las actividades")
async def consultaActividades(request : Request)->ActividadesSalida:
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.consultaGeneral()

@router.get("/{idActividad}", response_model=ActividadesSalidaID, summary="Consultar una actividad por su ID")
async def consultarActividadID(idActividad: str, request: Request) -> ActividadesSalidaID:
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.consultarActividadPorID(idActividad)
