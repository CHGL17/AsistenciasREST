from fastapi import APIRouter, Request, Depends
from models.asistenciasModel import AsistenciaInsert, AsistenciaSalida, AsistenciasSalida, Salida
from dao.asistenciasDAO import AsistenciaDAO
from dao.auth import require_roles, require_rol

router = APIRouter(
    prefix="/asistencias",
    tags=["Asistencias"]
)

@router.post("/", response_model=AsistenciaSalida, status_code=201, summary="Registrar una nueva asistencia")
async def registrarAsistencia(
    asistencia: AsistenciaInsert, 
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor"]))
) -> AsistenciaSalida:
    """
    Registrar una nueva asistencia - Coordinadores y Tutores
    """
    asistenciaDAO = AsistenciaDAO(request.app.db)
    return asistenciaDAO.agregar(asistencia)

@router.get("/", response_model=AsistenciasSalida, summary="Consultar todas las asistencias")
async def consultarAsistencias(
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor", "alumno"]))
) -> AsistenciasSalida:
    """
    Consultar todas las asistencias - Coordinadores, Tutores y Alumnos
    """
    asistenciaDAO = AsistenciaDAO(request.app.db)
    return asistenciaDAO.consultaGeneral()

@router.get("/{idAsistencia}", response_model=AsistenciaSalida, summary="Consultar una asistencia por su ID")
async def consultarAsistenciaPorID(
    idAsistencia: str, 
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor", "alumno"]))
) -> AsistenciaSalida:
    """
    Consultar una asistencia específica - Coordinadores, Tutores y Alumnos
    """
    asistenciaDAO = AsistenciaDAO(request.app.db)
    return asistenciaDAO.consultarAsistenciaPorID(idAsistencia)

@router.put("/{idAsistencia}", response_model=AsistenciaSalida, summary="Actualizar una asistencia")
async def actualizarAsistencia(
    idAsistencia: str, 
    asistencia: AsistenciaInsert, 
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor"]))
) -> AsistenciaSalida:
    """
    Actualizar una asistencia - Coordinadores y Tutores
    """
    asistenciaDAO = AsistenciaDAO(request.app.db)
    return asistenciaDAO.actualizar(idAsistencia, asistencia)

@router.patch("/{idAsistencia}/alumnos/{idAlumno}", response_model=AsistenciaSalida, summary="Agregar un alumno a la lista de asistencia")
async def agregarAlumnoAAsistencia(
    idAsistencia: str, 
    idAlumno: str, 
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor"]))
) -> AsistenciaSalida:
    """
    Agregar un alumno a la lista de asistencia - Coordinadores y Tutores
    """
    asistenciaDAO = AsistenciaDAO(request.app.db)
    return asistenciaDAO.agregarAlumnoAsistencia(idAsistencia, idAlumno)

@router.delete("/{idAsistencia}/alumnos/{idAlumno}", response_model=AsistenciaSalida, summary="Eliminar un alumno de la lista de asistencia")
async def eliminarAlumnoDeAsistencia(
    idAsistencia: str, 
    idAlumno: str, 
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor"]))
) -> AsistenciaSalida:
    """
    Eliminar un alumno de la lista de asistencia - Coordinadores y Tutores
    """
    asistenciaDAO = AsistenciaDAO(request.app.db)
    return asistenciaDAO.eliminarAlumnoAsistencia(idAsistencia, idAlumno)

@router.delete("/{idAsistencia}", response_model=Salida, summary="Cancelar una asistencia")
async def cancelarAsistencia(
    idAsistencia: str, 
    request: Request,
    current_user: dict = Depends(require_roles(["coordinador", "tutor"]))
) -> Salida:
    """
    Cancelar una asistencia - Coordinadores y Tutores
    """
    asistenciaDAO = AsistenciaDAO(request.app.db)
    return asistenciaDAO.cancelar(idAsistencia)