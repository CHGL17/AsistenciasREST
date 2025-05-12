from pymongo import MongoClient

DATABASE_URL = 'mongodb://localhost:27017/'
DATABASE_NAME = 'AsistenciasRest'

class Conexion:
    def __init__(self):
        self.cliente = MongoClient(DATABASE_URL)
        self.db = self.cliente[DATABASE_NAME]

    def cerrar(self):
        self.cliente.close()

    def getDB(self):
        return self.db