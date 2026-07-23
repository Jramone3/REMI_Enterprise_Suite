import sys
sys.path.insert(0, '.')
import traceback
try:
    # Esto ejecuta TODO el script como si lo hubieras llamado directamente
    exec(open('REMI/scripts/remi_responde.py').read())
    print("¡REMI TERMINÓ DE EJECUTARSE SIN ERRORES!")
except Exception as e:
    print("ERROR AL EJECUTAR EL SCRIPT:")
    traceback.print_exc()
