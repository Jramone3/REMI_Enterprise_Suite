import { useState, useRef, useEffect } from 'react';

export default function RemiChat() {
  const [mensaje, setMensaje] = useState('');
  const [imagenBase64, setImagenBase64] = useState(null);
  const [nombreArchivo, setNombreArchivo] = useState('');
  const [respuesta, setRespuesta] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Estados de interfaz y controles
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [escuchandoVoz, setEscuchandoVoz] = useState(false);
  const [modoAudioVega, setModoAudioVega] = useState(true); // Escuchar respuesta activado por defecto

  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Inicializar Reconocimiento de Voz (Web Speech API)
  useEffect(() => {
    if (typeof window !== 'undefined' && ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new SpeechRecognition();
      rec.lang = 'es-ES';
      rec.continuous = false;
      rec.interimResults = false;

      rec.onresult = (e) => {
        const textoEscuchado = e.results[0][0].transcript;
        setMensaje((prev) => (prev ? `${prev} ${textoEscuchado}` : textoEscuchado));
        setEscuchandoVoz(false);
      };

      rec.onerror = () => setEscuchandoVoz(false);
      rec.onend = () => setEscuchandoVoz(false);

      recognitionRef.current = rec;
    }
  }, []);

  // 1. Manejo de archivo / imagen (Iris)
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setNombreArchivo(file.name);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagenBase64(reader.result);
      };
      reader.readAsDataURL(file);
    }
    setMenuAbierto(false);
  };

  // 2. Manejo de Micrófono (Voz Entrada)
  const toggleMic = () => {
    setMenuAbierto(false);
    if (!recognitionRef.current) {
      alert("Tu navegador no soporta reconocimiento de voz nativo.");
      return;
    }
    if (escuchandoVoz) {
      recognitionRef.current.stop();
      setEscuchandoVoz(false);
    } else {
      setEscuchandoVoz(true);
      recognitionRef.current.start();
    }
  };

  // 3. Manejo de Toggle de Audio (Vega TTS)
  const toggleEscucharRespuesta = () => {
    setModoAudioVega(!modoAudioVega);
    setMenuAbierto(false);
  };

  // Función de envío principal a server.py (Puerto 5000)
  const enviar = async () => {
    if (!mensaje && !imagenBase64) return;
    setLoading(true);
    setRespuesta('REMI está procesando la solicitud desde el búnker...');

    try {
      const res = await fetch('http://localhost:5000/api/remi', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: mensaje,
          image: imagenBase64 || null,
          speak: modoAudioVega
        }),
      });
      const data = await res.json();
      const respTexto = data.response || data.message || JSON.stringify(data);
      setRespuesta(respTexto);

      // Si hay audio Base64 retornado en la respuesta, lo reproducimos en el navegador
      if (data.audio_b64) {
        const audio = new Audio(`data:audio/wav;base64,${data.audio_b64}`);
        audio.play().catch(e => console.log("Error de audio:", e));
      }
    } catch (err) {
      setRespuesta(`[ERROR DE CONEXIÓN PUERTO 5000]: ${err.message}`);
    } finally {
      setLoading(false);
      setImagenBase64(null);
      setNombreArchivo('');
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto', fontFamily: 'monospace', color: '#0ff', background: '#0a0a0a', border: '1px solid #333', borderRadius: '8px' }}>
      <h2>💬 REMI Enterprise Suite - Centro de Mando</h2>

      {/* Input de texto principal */}
      <div style={{ marginBottom: '15px' }}>
        <textarea
          rows="3"
          style={{ width: '100%', padding: '10px', background: '#111', color: '#fff', border: '1px solid #444', borderRadius: '4px' }}
          value={mensaje}
          onChange={(e) => setMensaje(e.target.value)}
          placeholder={escuchandoVoz ? "Escuchando tu voz..." : "Escribe o dicta tu instrucción..."}
        />
      </div>

      {/* Selector oculto de archivo */}
      <input 
        type="file" 
        ref={fileInputRef}
        accept="image/*" 
        onChange={handleFileChange} 
        style={{ display: 'none' }} 
      />

      {/* Barra de Herramientas y Menú desplegable Botón + */}
      <div style={{ marginBottom: '15px', position: 'relative', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <button 
          onClick={() => setMenuAbierto(!menuAbierto)}
          style={{ background: '#222', border: '1px solid #0ff', color: '#0ff', padding: '8px 15px', cursor: 'pointer', borderRadius: '4px', fontSize: '16px', fontWeight: 'bold' }}
        >
          ➕ Menú de Sentidos
        </button>

        {/* Indicadores de estado activos */}
        {nombreArchivo && <span style={{ fontSize: '12px', color: '#ff0' }}>📎 Imagen: {nombreArchivo}</span>}
        {escuchandoVoz && <span style={{ fontSize: '12px', color: '#f0f', animation: 'pulse 1s infinite' }}>🎤 Escuchando...</span>}
        <span style={{ fontSize: '12px', color: modoAudioVega ? '#0f0' : '#888' }}>
          🔊 Voz (Vega): {modoAudioVega ? 'ACTIVADA' : 'MUTED'}
        </span>

        {/* Desplegable de los 3 botones */}
        {menuAbierto && (
          <div style={{ position: 'absolute', top: '40px', left: '0', background: '#151515', border: '1px solid #555', borderRadius: '6px', zIndex: 100, display: 'flex', flexDirection: 'column', width: '220px', boxShadow: '0 4px 10px rgba(0,0,0,0.5)' }}>
            <button 
              onClick={() => { fileInputRef.current?.click(); }}
              style={{ padding: '10px', background: 'transparent', color: '#fff', border: 'none', borderBottom: '1px solid #333', textAlign: 'left', cursor: 'pointer' }}
            >
              📎 Adjuntar Archivo / Imagen
            </button>
            <button 
              onClick={toggleMic}
              style={{ padding: '10px', background: 'transparent', color: escuchandoVoz ? '#f0f' : '#fff', border: 'none', borderBottom: '1px solid #333', textAlign: 'left', cursor: 'pointer' }}
            >
              🎤 Micrófono (Voz {escuchandoVoz ? 'ON' : 'OFF'})
            </button>
            <button 
              onClick={toggleEscucharRespuesta}
              style={{ padding: '10px', background: 'transparent', color: modoAudioVega ? '#0f0' : '#aaa', border: 'none', textAlign: 'left', cursor: 'pointer' }}
            >
              🔊 Escuchar Respuesta ({modoAudioVega ? 'ON' : 'OFF'})
            </button>
          </div>
        )}
      </div>

      {/* Botón de envío */}
      <button 
        onClick={enviar} 
        disabled={loading}
        style={{ background: '#00aa55', color: '#fff', border: 'none', padding: '10px 20px', fontWeight: 'bold', cursor: 'pointer', borderRadius: '4px', width: '100%' }}
      >
        {loading ? 'Transmitiendo al Búnker...' : 'Enviar Petición a REMI'}
      </button>

      {/* Pantalla de respuesta de REMI */}
      <div style={{ marginTop: '20px', padding: '15px', background: '#121212', border: '1px solid #222', borderRadius: '4px', minHeight: '100px', whiteSpace: 'pre-wrap' }}>
        <strong>Respuesta de REMI:</strong>
        <p>{respuesta}</p>
      </div>
    </div>
  );
}
