import uvicorn
from fastapi import FastAPI
from dao.database import Conexion
from routers import usuariosRouter, actividadesRouter,ciclosRouters,carrerasRouter

app = FastAPI()

# Incluir routers
app.include_router(usuariosRouter.router)
app.include_router(actividadesRouter.router)
app.include_router(ciclosRouters.router)
app.include_router(carrerasRouter.router)

@app.get("/")
async def root():
    return {"mensaje": "Bienvenido a AsistenciasREST"}

@app.on_event("startup")
async def startup():
    print("Conectando con MongoDB")
    conexion = Conexion()
    app.conexion = conexion
    app.db = conexion.getDB()

@app.on_event("shutdown")
async def shutdown():
    print("Cerrando la conexión con MongoDB")
    app.conexion.cerrar()

#python -m main uvicorn main:app --reload
if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', reload=True)