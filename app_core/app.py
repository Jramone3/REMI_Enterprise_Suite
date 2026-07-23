from flask import Flask, request, jsonify
from flask_cors import CORS
from s3_auditor import audit_s3_config_text
from database import log_audit, get_audit_stats

app = Flask(__name__)
CORS(app)

@app.route('/audit', methods=['POST'])
def audit_config():
    data = request.get_json(silent=True)
    
    if not data or 'config' not in data:
        return jsonify({
            "status": "ERROR",
            "secure": False,
            "message": "Formato de petición inválido. Se requiere un JSON con la clave 'config'."
        }), 400

    config_content = data['config']
    
    # Ejecutamos el auditor estático
    resultado = audit_s3_config_text(config_content)
    
    # Registramos la auditoría de forma persistente en SQLite
    log_audit(
        status=resultado.get("status"),
        secure=resultado.get("secure"),
        findings=resultado.get("findings", []),
        raw_config=config_content
    )
    
    return jsonify(resultado)

@app.route('/stats', methods=['GET'])
def audit_stats():
    """Endpoint de analítica para ver métricas globales del búnker."""
    stats = get_audit_stats()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
