from fastapi import APIRouter, Request, HTTPException
from models.carrerasModel import CarreraInsert, CarreraUpdate, CarreraSalida, CarrerasSalida
from dao.carrerasDao import CarreraDAO

router = APIRouter(
    prefix="/carreras",
    tags=["Carreras"]
)

@router.post("/", response_model=CarreraSalida, status_code=201, summary="Crear una nueva carrera")
async def crear_carrera(carrera: CarreraInsert, request: Request) -> CarreraSalida:
    carrera_dao = CarreraDAO(request.app.db)
    return await carrera_dao.agregar_carrera(carrera)

@router.get("/", response_model=CarrerasSalida, summary="Consultar todas las carreras")
async def consultar_carreras(request: Request) -> CarrerasSalida:
    carrera_dao = CarreraDAO(request.app.db)
    return await carrera_dao.consulta_general_carreras()

@router.get("/{carrera_id}", response_model=CarreraSalida, summary="Consultar una carrera por su ID")
async def consultar_carrera_por_id(carrera_id: int, request: Request) -> CarreraSalida:
    carrera_dao = CarreraDAO(request.app.db)
    return await carrera_dao.consultar_carrera_por_id(carrera_id)

@router.put("/{carrera_id}", response_model=CarreraSalida, summary="Actualizar una carrera")
async def actualizar_carrera(carrera_id: int, carrera: CarreraUpdate, request: Request) -> CarreraSalida:
    carrera_dao = CarreraDAO(request.app.db)
    return await carrera_dao.actualizar_carrera(carrera_id, carrera)

@router.delete("/{carrera_id}", response_model=CarreraSalida, summary="Eliminar una carrera")
async def eliminar_carrera(carrera_id: int, request: Request) -> CarreraSalida:
    carrera_dao = CarreraDAO(request.app.db)
    return await carrera_dao.eliminar_carrera(carrera_id)