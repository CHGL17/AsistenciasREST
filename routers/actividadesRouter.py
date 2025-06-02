from fastapi import APIRouter, Request, HTTPException, Depends
from models.actividadesModel import ActividadInsert, Salida, ActividadesSalida, ActividadSelectID, ActividadesSalidaID, TutorAsignacion
from dao.actividadesDAO import ActividadDAO
from dao.auth import require_rol, require_roles

router = APIRouter(
    prefix="/actividades",
    tags=["Actividades"]
)

@router.post("/", response_model=Salida, summary="Crear una nueva actividad")
async def crearActividad(
    actividad: ActividadInsert, 
    request: Request,
    current_user: dict = Depends(require_rol("coordinador"))
) -> Salida:
    """
    Crear una nueva actividad - Solo coordinadores
    """
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.agregar(actividad)

@router.get("/", response_model=ActividadesSalida, summary="Consultar todas las actividades")
async def consultaActividades(
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor", "alumno"]))
) -> ActividadesSalida:
    """
    Consultar todas las actividades - Coordinadores, Tutores y Alumnos
    """
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.consultaGeneral()

@router.get("/{idActividad}", response_model=ActividadesSalidaID, summary="Consultar una actividad por su ID")
async def consultarActividadID(
    idActividad: str, 
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor", "alumno"]))
) -> ActividadesSalidaID:
    """
    Consultar una actividad específica - Coordinadores, Tutores y Alumnos
    """
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.consultarActividadPorID(idActividad)

@router.put("/{idActividad}", response_model=ActividadesSalidaID, summary="Actualizar una actividad")
async def actualizarActividad(
    idActividad: str, 
    actividad: ActividadInsert, 
    request: Request,
    current_user: dict = Depends(require_rol("coordinador"))
) -> ActividadesSalidaID:
    """
    Actualizar una actividad - Solo Coordinadores
    """
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.actualizar(idActividad, actividad)

@router.patch("/{idActividad}/asignar-tutor", response_model=ActividadesSalidaID, summary="Asignar tutor a una actividad")
async def asignar_tutor_actividad(
    idActividad: str, 
    tutor_asignacion: TutorAsignacion, 
    request: Request,
    current_user: dict = Depends(require_rol("coordinador"))
) -> ActividadesSalidaID:
    """
    Asignar tutor a una actividad - Solo Coordinadores
    """
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.asignar_tutor(idActividad, tutor_asignacion)

@router.delete("/{idActividad}", response_model=Salida, summary="Cancelar una actividad")
async def cancelarActividad(
    idActividad: str, 
    request: Request,
    current_user: dict = Depends(require_rol("coordinador"))
) -> Salida:
    """
    Cancelar una actividad - Solo Coordinadores
    """
    actividadDAO = ActividadDAO(request.app.db)
    return actividadDAO.cancelar(idActividad)