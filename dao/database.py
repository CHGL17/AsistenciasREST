from pymongo import MongoClient

class Conexion:
    def __init__(self):
        self.cliente = MongoClient("mongodb://root:2GMI5DBwFI9PY13nDyyTYmmsRVifameoZ3Vry24LXsXW646OAEwHhrTgB48mRldj@159.54.150.147:27017/?directConnection=true")
        self.db = self.cliente["AsistenciasFastAPI"]  # Cambia "asistencias" por el nombre real de tu DB

    def getDB(self):
        return self.db

    def cerrar(self):
        self.cliente.close()
