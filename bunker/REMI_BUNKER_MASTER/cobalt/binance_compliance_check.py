from datetime import datetime

# Base de datos completa de restricciones oficiales de Binance (agosto de 2026)
RESTRICTED_ENTITIES = {
    "2026-08-07": [
        "Shelbit", "Shelbit General Trading LLC", "Aban Tether Exchange"
    ],
    "2026-08-13": [
        "A7 Nigeria", "A7 Africa", "PilotFinance Ltd"
    ],
    "2026-08-23": [
        "HTX", "Huobi Global SA", "EXMO", "EXMO Ltd", "Rapira", 
        "Aifory Pro", "Sooty Ltd", "ABCeX", "Nueva Cryptologia S.A.S. DE C.V.",
        "WhiteBird", "NoOnecrypto", "NoOnecrypto INC.", "Tradex", "Brightum LLC",
        "Monease", "Monease Ltd", "BitPapa", "Exnode", "Exnode Pay", "Arvix"
    ]
}

def check_entity(query_name):
    query_lower = query_name.lower().strip()
    found = False
    today = datetime.now().date()
    
    print(f"\n[Compliance Scan] Consultando: '{query_name}' (Fecha actual: {today})")
    print("-" * 65)
    
    for date_str, entities in RESTRICTED_ENTITIES.items():
        effective_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        is_active = today >= effective_date
        
        for entity in entities:
            if query_lower in entity.lower() or entity.lower() in query_lower:
                found = True
                status_msg = "ACTIVA Y VIGENTE" if is_active else "PROGRAMADA (Aún no efectiva)"
                print(f"-> Coincidencia encontrada: {entity}")
                print(f"   Estado: [{status_msg}]")
                print(f"   Fecha de restricción: {date_str}")
                print("-" * 65)
                
    if not found:
        print(" [OK] La entidad no figura en las listas de restricciones evaluadas.")
        print("-" * 65)

if __name__ == "__main__":
    target = input("Introduce el nombre de la plataforma o servicio a verificar: ").strip()
    if target:
        check_entity(target)
    else:
        print("No se ingresó ningún nombre para verificar.")
