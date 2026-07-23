import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';

export default function handler(req, res) {
  if (req.method !== 'POST') {
    res.status(405).json({ respuesta: 'Método no permitido' });
    return;
  }

  const mensaje = req.body.mensaje || "";
  const scriptPath = path.join(process.cwd(), 'pipeline_remi.py');
  const logPath = "os.path.expanduser("~/") + REMI_CORE/bunker/REMI/ARCHIVOS_PERSONALES_RAMON/Proyecto_Remi_IA_App/REMI_CHATS/remi_output.log";

  // Función para obtener logs
  const obtenerLogs = () => {
    try {
      return fs.readFileSync(logPath, 'utf8');
    } catch (e) {
      return "Error leyendo logs.";
    }
  };

  // Ejecutar el script si el usuario pide sincronizar o auditoría
  if (mensaje.toLowerCase().includes("sincronizar") || mensaje.toLowerCase().includes("auditoría")) {
    exec(`python3 ${scriptPath} run`, (error, stdout, stderr) => {
      const logsActualizados = obtenerLogs();
      if (error || stderr) {
        res.status(500).json({ 
          respuesta: `Error del Núcleo: ${stderr || error.message}`,
          telemetria: logsActualizados 
        });
        return;
      }
      res.status(200).json({ 
        respuesta: stdout.trim() || "Operación completada.",
        telemetria: logsActualizados 
      });
    });
  } else {
    // Respuesta estándar
    res.status(200).json({ 
      respuesta: "Mensaje recibido. Para actualizar el Búnker, escribe 'sincronizar'.",
      telemetria: obtenerLogs()
    });
  }
}
