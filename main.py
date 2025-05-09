from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.on_event("startup")
async def startup():
    print("Conectando con ")

@app.on_event("shutdown")
async def shutdown():
    print("Cerrando la conexion con ")