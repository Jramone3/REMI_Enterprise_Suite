from pymongo import MongoClient
import json

uri = "mongodb+srv://jramonrivasg_db_user:Jrrg2025Code@cluster0.loewdkg.mongodb.net/remi_memoria?retryWrites=true&w=majority"
client = MongoClient(uri)

db = client["remi_memoria"]
coleccion = db["trazas_patronales"]

trazas = list(coleccion.find())
with open("os.path.expanduser("~/") + documentacion/trazas_remi_exportadas.json", "w") as archivo:
    json.dump(trazas, archivo, default=str, indent=4)

print("Exportación completada.")
