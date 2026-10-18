import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuración de la ruta base del búnker en sda5
BASE_DIR = "/home/ramon/REMI_CORE/nucleo_activo/"

@app.route('/escribir_archivo', methods=['POST'])
def escribir_archivo():
    data = request.get_json()
    
    if not data or 'nombre' not in data or 'contenido' not in data:
        return jsonify({"status": "error", "message": "Datos incompletos. Falta 'nombre' o 'contenido'."}), 400
    
    nombre_archivo = data['nombre']
    contenido = data['contenido']
    
    # Validar que no se intente salir de la ruta segura (Path Traversal)
    if ".." in nombre_archivo or nombre_archivo.startswith("/"):
        return jsonify({"status": "error", "message": "Intento de violación de ruta no permitido."}), 400

    ruta_completa = os.path.join(BASE_DIR, nombre_archivo)
    
    try:
        # Asegurar que el directorio físico exista en sda5
        os.makedirs(BASE_DIR, exist_ok=True)
        
        # Escritura física y real en disco
        with open(ruta_completa, 'w', encoding='utf-8') as archivo:
            archivo.write(contenido)
            
        print(f"[REMI IO] Archivo escrito con éxito en: {ruta_completa}")
        return jsonify({
            "status": "success", 
            "message": f"Archivo '{nombre_archivo}' materializado físicamente en sda5."
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Corre localmente en el puerto 5000
    app.run(host='127.0.0.1', port=5005, debug=False)
