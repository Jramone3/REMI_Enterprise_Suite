import sys
from pymongo import MongoClient

print("--- MOTOR QUIRÚRGICO DE ALTA PRIORIDAD (REMI CORE) ---")
usuario = input("Usuario Atlas: ").strip()
password = input("Contraseña: ").strip()

MONGO_URI = f"mongodb+srv://{usuario}:{password}@cluster0.loewdkg.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db = client['remi_memoria']
    coleccion = db['trazas_patronales']
    
    while True:
        print("\n==================================================")
        print("    MENÚ DE RASTREO PATRIMONIAL MASIVO")
        print("==================================================")
        print("1. Rastrear por ID Patrimonial Exacto (ej. REMI-2026-65000)")
        print("2. Escanear Rango de IDs (ej. Del 64990 al 65000)")
        print("3. Rastrear por Origen de Archivo (ej. recup_dir.464)")
        print("4. Volver al búnker (Salir)")
        
        opcion = input("\nSelecciona tu vector de búsqueda (1-4): ").strip()
        
        if opcion == "1":
            id_pat = input("\nIntroduce el ID Patrimonial exacto: ").strip()
            doc = coleccion.find_one({"id_patrimonial": id_pat})
            if doc:
                print(f"\n🎯 [¡ENCONTRADO!] Metadatos de la Traza:")
                for k, v in doc.items():
                    print(f"  🔹 {k}: {v}")
            else:
                print(f"\n❌ No existe ningún registro con el ID: {id_pat}")
                
        elif opcion == "2":
            try:
                inicio = int(input("\nNúmero de inicio (ej. 64990): "))
                fin = int(input("Número de fin (ej. 65000): "))
                
                # Construimos la lista de IDs basados en tu formato REMI-2026-XXXXX
                lista_ids = [f"REMI-2026-{i}" for i in range(inicio, fin + 1)]
                
                print(f"\n⏳ Extrayendo bloque indexado ({len(lista_ids)} registros)...")
                resultados = coleccion.find({"id_patrimonial": {"$in": lista_ids}})
                
                conteo = 0
                for doc in resultados:
                    print(f"  📦 [{doc.get('id_patrimonial')}] | Origen: {doc.get('origen')} | Estado: {doc.get('estado')}")
                    conteo += 1
                print(f"\n✅ Escaneo finalizado. {conteo} registros mostrados en pantalla.")
            except ValueError:
                print("\n⚠️ Por favor, introduce solo números enteros.")
                
        elif opcion == "3":
            origen = input("\nIntroduce el origen a rastrear (ej. recup_dir.464): ").strip()
            print(f"\n🔍 Buscando las primeras 10 muestras con origen '{origen}'...")
            resultados = coleccion.find({"origen": origen}).limit(10)
            
            conteo = 0
            for doc in resultados:
                print(f"  📍 ID: {doc.get('id_patrimonial')} | Timestamp: {doc.get('timestamp')}")
                conteo += 1
            if conteo == 0:
                print("\n❌ No se encontraron registros asociados a ese origen.")
                
        elif opcion == "4":
            print("\nPuente cerrado. Saliendo del núcleo.")
            break
        else:
            print("\n⚠️ Opción inválida.")

except Exception as e:
    print(f"\n[ERROR CRÍTICO]: {e}")
