from models.actividadesModel import ActividadInsert, Salida, ActividadesSalida, ActividadSelectID, ActividadesSalidaID
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

class ActividadDAO:
    def __init__(self, db):
        self.db = db

    async def agregar(self, actividad: ActividadInsert, usuario_actual):
        salida = Salida(estatus="", mensaje="")
        if usuario_actual.tipo != "coordinador":
            salida.estatus = "ERROR"
            salida.mensaje = "Solo los coordinadores pueden crear actividades"
            return salida

        ubicacion = await self.db.ubicaciones.find_one({"_id": ObjectId(actividad.ubicacion)})
        if not ubicacion:
            salida.estatus = "ERROR"
            salida.mensaje = "La ubicación especificada no existe"
            return salida

        nueva_actividad = jsonable_encoder(actividad)
        nueva_actividad["tutor"] = None

        resultado = await self.db.actividades.insert_one(nueva_actividad)

        if resultado.inserted_id:
            actividad_creada = await self.db.actividades.find_one(
                {"_id": resultado.inserted_id}
            )
            salida.estatus = "OK"
            salida.mensaje = "Actividad creada exitosamente"
            return {
                "salida": salida,
                "actividad": actividad_creada
            }
        else:
            salida.estatus = "ERROR"
            salida.mensaje = "Error al crear la actividad"
            return salida

    def consultaGeneral(self):
        salida = ActividadesSalida(estatus="", mensaje="", actividades=[])
        try:
            lista = list(self.db.actividades.find())
            salida.estatus = "OK"
            salida.mensaje = "Listado de actividades."
            salida.actividades = lista
        except Exception as ex:
            print(ex)
            salida.estatus = "ERROR"
            salida.mensaje = "Error al consultar las actividades, consulta al adminstrador."
        return salida

    def consultarActividadPorID(self, idActividad: str) -> ActividadesSalidaID:
        salida = ActividadesSalidaID(estatus="", mensaje="", actividad=None)
        try:
            actividad_data = self.db.actividades.find_one({"_id": idActividad})
            if actividad_data:
                salida.actividad = actividad_data
                salida.estatus = "OK"
                salida.mensaje = f"Actividad {idActividad} encontrada con extito."
            else:
                salida.estatus = "ERROR"
                salida.mensaje = f"La actividad con id {idActividad} no se ha encontrado."
        except Exception as e:
                print(f"Error al consultar la actividad {idActividad}: {e}")
                salida.estatus = "ERROR"
                salida.mensaje = "Error interno al consultar la actividad."
        return salida
