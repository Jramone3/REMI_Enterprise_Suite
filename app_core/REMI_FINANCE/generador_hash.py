import hashlib
import sys

def generar_hash(texto):
    return hashlib.sha256(texto.encode()).hexdigest()

if __name__ == "__main__":
    reporte = sys.argv[1]
    print(f"Tu Hash único es: {generar_hash(reporte)}")
