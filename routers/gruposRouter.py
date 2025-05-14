from fastapi import APIRouter, Request, HTTPException
from models.gruposModel import GrupoInsert, GrupoUpdate, Salida, GrupoSalida, GruposSalida
from dao.gruposDAO import GrupoDAO

router = APIRouter(
    prefix="/grupos",
    tags=["Grupos"]
)

@router.post("/", response_model=GrupoSalida, status_code=201, summary="Crear un nuevo grupo")
async def crearGrupo(grupo: GrupoInsert, request: Request) -> GrupoSalida:
    # try:
    #     usuario_actual = request.state.usuario
    #     if usuario_actual.tipo != "coordinador":
    #         raise HTTPException(
    #             status_code=403,
    #             detail="Solo los coordinadores pueden crear grupos"
    #         )
    # except AttributeError:
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Se requiere autenticación para crear grupos"
    #     )
        
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.agregar(grupo)

@router.get("/", response_model=GruposSalida, summary="Consultar todos los grupos")
async def consultarGrupos(request: Request) -> GruposSalida:
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.consultaGeneral()

@router.get("/semestre/{semestre}", response_model=GruposSalida, summary="Consultar grupos por semestre")
async def consultarGruposPorSemestre(semestre: int, request: Request) -> GruposSalida:
    # Validar que el semestre sea válido (1-9)
    if semestre < 1 or semestre > 9:
        raise HTTPException(
            status_code=400,
            detail="El semestre debe estar entre 1 y 9"
        )
        
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.consultarPorSemestre(semestre)

@router.get("/{idGrupo}", response_model=GrupoSalida, summary="Consultar un grupo por su ID")
async def consultarGrupoPorID(idGrupo: str, request: Request) -> GrupoSalida:
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.consultarPorID(idGrupo)

@router.put("/{idGrupo}", response_model=GrupoSalida, summary="Actualizar un grupo")
async def actualizarGrupo(idGrupo: str, grupo: GrupoUpdate, request: Request) -> GrupoSalida:
    print(f"Actualizar grupo {idGrupo} con datos: {grupo}")
    try:
        usuario_actual = request.state.usuario
        if usuario_actual.tipo != "coordinador":
            raise HTTPException(
                status_code=403,
                detail="Solo los coordinadores pueden actualizar grupos"
            )
    except AttributeError:
        raise HTTPException(
            status_code=401,
            detail="Se requiere autenticación para actualizar grupos"
        )
        
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.actualizar(idGrupo, grupo)

@router.delete("/{idGrupo}", response_model=Salida, summary="Eliminar un grupo")
async def eliminarGrupo(idGrupo: str, request: Request) -> Salida:
    try:
        usuario_actual = request.state.usuario
        if usuario_actual.tipo != "coordinador":
            raise HTTPException(
                status_code=403,
                detail="Solo los coordinadores pueden eliminar grupos"
            )
    except AttributeError:
        raise HTTPException(
            status_code=401,
            detail="Se requiere autenticación para eliminar grupos"
        )
        
    grupoDAO = GrupoDAO(request.app.db)
    return await grupoDAO.eliminar(idGrupo)