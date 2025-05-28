from pymongo import MongoClient

class Conexion:
    def __init__(self):
        self.cliente = MongoClient("mongodb+srv://l21010280:pQKdAFOhBKXhc76x@asistenciasitesz.mmfv6a2.mongodb.net/?retryWrites=true&w=majority&appName=AsistenciasITESZ")
        self.db = self.cliente["AsistenciasBD"]

    def getDB(self):
        return self.db

    def cerrar(self):
        self.cliente.close()
