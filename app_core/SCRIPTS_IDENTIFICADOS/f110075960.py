import sys
sys.path.insert(0, '.')
import traceback
try:
    import REMI.scripts.remi_responde
    print("¡ÉXITO! El módulo se importó sin errores")
except Exception as e:
    print("ERROR ENCONTRADO:")
    traceback.print_exc()
    raise
