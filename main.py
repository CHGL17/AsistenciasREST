import uvicorn
from fastapi import FastAPI
from pymongo import MongoClient

from dao.database import Conexion
from routers import actividadesRouter

#Crear una instancia de la clase fastapi
app = FastAPI()

app.include_router(actividadesRouter.router)
@app.get("/")
async def root():
    salida = {"mensaje": "Bienvenido a AsistenciasREST"}
    return salida

@app.on_event("startup")
async def startup():
    print("Conectando con ")
    conexion = Conexion()
    app.conexion = conexion
    app.db = conexion.getDB()

@app.on_event("shutdown")
async def shutdown():
    print("Cerrando la conexion con ")
    app.conexion.cerrar()

if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', reload=True)