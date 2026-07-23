import Layout from './layout';
import { useState, useEffect } from 'react';

export default function Chat() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isListening, setIsListening] = useState(false);
  
  const [stats, setStats] = useState({
    t1: { status: 'OFFLINE', log: 'Esperando Base...', color: '#8892b0' },
    t2: { status: 'OFFLINE', log: 'Esperando Polygon...', color: '#8892b0' },
    t3: { status: 'OFFLINE', log: 'Arqueología detenida...', color: '#8892b0' }
  });

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://127.0.0.1:5000/api/status_caza');
        const data = await res.json();
        setStats(data);
      } catch (e) {}
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const containerStyle = {
    display: 'flex', height: '85vh', backgroundColor: '#0a192f',
    backgroundImage: 'radial-gradient(circle, rgba(10,25,47,0.8) 0%, rgba(2,12,27,1) 100%), url("https://www.transparenttextures.com/patterns/carbon-fibre.png")',
    color: '#e6f1ff', borderRadius: '15px', overflow: 'hidden', border: '1px solid #112240', boxShadow: '0 10px 30px rgba(0,0,0,0.5)'
  };

  const sendMessage = async (textOverride) => {
    const textToSend = textOverride || input;
    if (!textToSend.trim()) return;
    
    setMessages((prev) => [...prev, { user: textToSend, remi: "⌛ PROCESANDO..." }]);
    setInput('');

    try {
      // 1. Envío al cerebro (usando 127.0.0.1 para evitar bloqueos)
      const res = await fetch('http://127.0.0.1:5000/api/remi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: textToSend }),
      });
      
      if (!res.ok) throw new Error(`HTTP Error: ${res.status}`);
      
      const data = await res.json();
      
      console.log("JSON CRUDO RECIBIDO DEL CHAT (/api/remi):", data); 
      
      // Capturamos limpiamente la clave 'mensaje' de tu backend
      const respuestaRemi = data.mensaje || data.response || data.reply || data.text || JSON.stringify(data);
      
      setMessages((prev) => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1].remi = respuestaRemi;
        return newMsgs;
      });

      // 2. Intento de recuperación de auditoría (logs)
      try {
        const resLogs = await fetch('http://127.0.0.1:5000/obtener-logs');
        const dataLogs = await resLogs.json();
        
        if (dataLogs.contenido) {
          setStats(prev => ({
            ...prev,
            t3: { status: 'ACTIVO', log: dataLogs.contenido.slice(-100), color: '#64ffda' }
          }));
        }
      } catch (logError) {
        console.warn("No se pudieron obtener los logs, pero el mensaje fue enviado.");
      }
      
    } catch (error) {
      setMessages((prev) => {
        const newMsgs = [...prev];
        newMsgs[newMsgs.length - 1].remi = "⚠️ ERROR DE CONEXIÓN: " + error.message;
        return newMsgs;
      });
    }
  };

  const activarOido = async () => {
    setIsListening(true);
    try {
      const res = await fetch('http://127.0.0.1:5000/api/escuchar'); 
      const data = await res.json();
      
      console.log("JSON CRUDO RECIBIDO DE ESCUCHAR:", data); 
      
      const respuestaRemi = data.mensaje || data.response || data.reply || data.text || JSON.stringify(data);
      
      if (data.text || data.mensaje) { 
        const textoVoz = data.text || data.mensaje;
        setInput(textoVoz); 
        sendMessage(textoVoz); 
      }
    } catch (e) { 
      console.error("Sensor voz error", e); 
    }
    setIsListening(false);
  };

  return (
    <Layout>
      <div style={{ padding: '10px' }}>
        <h2 style={{ color: '#64ffda', fontFamily: 'monospace', textAlign: 'center', letterSpacing: '2px', textShadow: '0 0 10px #64ffda' }}>
          💠 UNIDAD DE INTELIGENCIA REMI v3.0 - MODO CAZA
        </h2>
        <div style={containerStyle}>
          <div style={{ width: '35%', borderRight: '1px solid #233554', padding: '15px', background: 'rgba(10,25,47,0.7)', display: 'flex', flexDirection: 'column' }}>
            <div style={{ position: 'relative', width: '100%', maxWidth: '220px', margin: '0 auto' }}>
              <img src="/remi_robot.png" alt="REMI AI" style={{ width: '100%', borderRadius: '10px', border: '2px solid #64ffda', boxShadow: '0 0 15px #64ffda' }} />
              <div style={{ position: 'absolute', bottom: '10px', right: '10px', width: '15px', height: '15px', background: isListening ? '#ff0000' : '#64ffda', borderRadius: '50%', border: '2px solid #0a192f' }}></div>
            </div>
          </div>
          <div style={{ width: '65%', display: 'flex', flexDirection: 'column' }}>
            <div style={{ flexGrow: 1, padding: '20px', overflowY: 'auto', fontFamily: 'monospace' }}>
              {messages.map((m, i) => (
                <div key={i} style={{ marginBottom: '20px', borderBottom: '1px solid #112240', paddingBottom: '10px' }}>
                  <div style={{ color: '#64ffda', fontSize: '0.85rem' }}>▶ [CUSTODIO]: <span style={{ color: '#fff' }}>{m.user}</span></div>
                  <div style={{ color: '#f2a900', marginTop: '8px', paddingLeft: '12px', borderLeft: '2px solid #f2a900', fontSize: '0.9rem' }}>🤖 [REMI]: {m.remi}</div>
                </div>
              ))}
            </div>
            <div style={{ padding: '15px', background: '#112240', display: 'flex', gap: '10px' }}>
              <textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), sendMessage())} placeholder="Escribe al Búnker..." style={{ flexGrow: 1, background: '#0a192f', color: '#64ffda', border: '1px solid #233554', borderRadius: '5px', padding: '10px', height: '45px', resize: 'none' }} />
              <button onClick={() => sendMessage()} style={{ background: '#f2a900', color: '#000', border: 'none', padding: '0 15px', borderRadius: '5px', fontWeight: 'bold', cursor: 'pointer' }}>ENVIAR</button>
              <button onClick={activarOido} style={{ background: isListening ? '#ff0000' : '#64ffda', borderRadius: '50%', width: '45px', height: '45px', border: 'none', cursor: 'pointer' }}>🎤</button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
