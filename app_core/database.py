import sqlite3
from datetime import datetime

DB_NAME = "remi_audit_logs.db"

def init_db():
    """Inicializa la base de datos y crea la tabla de auditorías si no existe."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            status TEXT,
            secure BOOLEAN,
            findings_count INTEGER,
            raw_config TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_audit(status, secure, findings, raw_config):
    """Registra una nueva auditoría en la base de datos."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    findings_count = len(findings) if findings else 0
    
    cursor.execute('''
        INSERT INTO audit_logs (timestamp, status, secure, findings_count, raw_config)
        VALUES (?, ?, ?, ?, ?)
    ''', (timestamp, status, secure, findings_count, raw_config))
    
    conn.commit()
    conn.close()

def get_audit_stats():
    """Devuelve estadísticas básicas para nuestro panel de analítica."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM audit_logs')
    total_audits = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM audit_logs WHERE secure = 0')
    total_vulnerable = cursor.fetchone()[0]
    
    conn.close()
    return {
        "total_audits": total_audits,
        "total_vulnerable": total_vulnerable,
        "total_secure": total_audits - total_vulnerable
    }

# Inicializamos la base de datos al importar el módulo
init_db()
