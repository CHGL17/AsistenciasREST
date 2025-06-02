from fastapi import APIRouter, Request, HTTPException, Depends
from models.gruposModel import GrupoInsert, GrupoUpdate, Salida, GrupoSalida, GruposSalida
from dao.gruposDAO import GrupoDAO
from dao.auth import require_coordinador # Import the dependency

router = APIRouter(
    prefix="/grupos",
    tags=["Grupos"]
)

@router.post("/", response_model=GrupoSalida, status_code=201, summary="Crear un nuevo grupo")
async def crearGrupo(grupo: GrupoInsert, request: Request, current_user: dict = Depends(require_coordinador)) -> GrupoSalida:
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.agregar(grupo)

@router.get("/", response_model=GruposSalida, summary="Consultar todos los grupos")
async def consultarGrupos(request: Request, current_user: dict = Depends(require_coordinador)) -> GruposSalida:
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.consultaGeneral()

@router.get("/semestre/{semestre}", response_model=GruposSalida, summary="Consultar grupos por semestre")
async def consultarGruposPorSemestre(semestre: int, request: Request, current_user: dict = Depends(require_coordinador)) -> GruposSalida:
    # Validar que el semestre sea válido (1-9)
    if semestre < 1 or semestre > 9:
        raise HTTPException(
            status_code=400,
            detail={"estatus": "ERROR", "mensaje": "El semestre debe estar entre 1 y 9"}
        )
        
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.consultarPorSemestre(semestre)

@router.get("/{idGrupo}", response_model=GrupoSalida, summary="Consultar un grupo por su ID")
async def consultarGrupoPorID(idGrupo: str, request: Request, current_user: dict = Depends(require_coordinador)) -> GrupoSalida:
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.consultarPorID(idGrupo)

@router.put("/{idGrupo}", response_model=GrupoSalida, summary="Actualizar un grupo")
async def actualizarGrupo(idGrupo: str, grupo: GrupoUpdate, request: Request, current_user: dict = Depends(require_coordinador)) -> GrupoSalida:
    print(f"Actualizar grupo {idGrupo} con datos: {grupo}")

    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.actualizar(idGrupo, grupo)

@router.delete("/{idGrupo}", response_model=Salida, summary="Eliminar un grupo")
async def eliminarGrupo(idGrupo: str, request: Request, current_user: dict = Depends(require_coordinador)) -> Salida:

    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.eliminar(idGrupo)

@router.patch("/{idGrupo}/alumnos/{idAlumno}", response_model=GrupoSalida, summary="Agregar un alumno al grupo")
async def agregarAlumnoAGrupo(idGrupo: str, idAlumno: str, request: Request, current_user: dict = Depends(require_coordinador)) -> GrupoSalida:
        
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.agregarAlumno(idGrupo, idAlumno)

@router.delete("/{idGrupo}/alumnos/{idAlumno}", response_model=GrupoSalida, summary="Eliminar un alumno del grupo")
async def eliminarAlumnoDeGrupo(idGrupo: str, idAlumno: str, request: Request, current_user: dict = Depends(require_coordinador)) -> GrupoSalida:
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.eliminarAlumno(idGrupo, idAlumno)