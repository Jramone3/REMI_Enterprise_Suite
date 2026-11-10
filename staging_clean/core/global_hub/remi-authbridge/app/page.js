'use client';

import { useState, useRef, useEffect } from 'react';

export default function Home() {
  const [mensaje, setMensaje] = useState('');
  const [imagenBase64, setImagenBase64] = useState(null);
  const [nombreArchivo, setNombreArchivo] = useState('');
  const [chats, setChats] = useState([
    { remite: 'remi', texto: 'Saludos, Ramón. Núcleo ceremonial y cognitivo resintonizado. Percepción óptica lista. ¿Qué evaluamos hoy?' }
  ]);
  const [loading, setLoading] = useState(false);

  // Estados de interfaz y controles de sentidos
  const [menuAbierto, setMenuAbierto] = useState(false);
  const [escuchandoVoz, setEscuchandoVoz] = useState(false);
  const [modoAudioVega, setModoAudioVega] = useState(true);

  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);
  const chatEndRef = useRef(null);

  // Autoscroll del chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chats]);

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

  // 1. Manejo de archivo / imagen (Iris) con Preview Visual
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setNombreArchivo(file.name);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagenBase64(reader.result); // Base64 completo con previsualización
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

  // Función de envío principal al servidor del búnker (Puerto 5000)
  const enviar = async () => {
    if (!mensaje && !imagenBase64) return;
    
    const mensajeUsuario = mensaje;
    const base64Payload = imagenBase64;
    const archivoActual = nombreArchivo;

    // Actualizamos la UI con el mensaje del usuario y miniatura opcional
    setChats((prev) => [...prev, { 
      remite: 'usuario', 
      texto: mensajeUsuario, 
      imagen: base64Payload,
      nombreArchivo: archivoActual 
    }]);
    
    setMensaje('');
    setImagenBase64(null);
    setNombreArchivo('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:5000/api/remi', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: mensajeUsuario,
          image: base64Payload, // Enviamos el Base64 de la imagen a Iris
          speak: modoAudioVega,
          lang: 'es'
        })
      });

      const data = await res.json();
      const respuestaRemi = data.response || data.message || JSON.stringify(data);

      setChats((prev) => [...prev, { remite: 'remi', texto: respuestaRemi }]);

      // Si hay audio Base64 retornado, lo reproducimos
      if (data.audio_b64) {
        const audio = new Audio(`data:audio/wav;base64,${data.audio_b64}`);
        audio.play().catch(e => console.log("Error de audio:", e));
      }
    } catch (err) {
      setChats((prev) => [...prev, { remite: 'remi', texto: `[ERROR DE CONEXIÓN PUERTO 5000]: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ minHeight: '100vh', background: '#060913', color: '#f8fafc', padding: '1.5rem', fontFamily: 'monospace' }}>
      
      {/* Cabecera Soberana */}
      <header style={{ marginBottom: '1.5rem', borderBottom: '1px solid #1e293b', paddingBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '1.4rem', color: '#38bdf8', margin: 0 }}>🛡️ REMI Enterprise Suite - Centro de Mando Soberano</h1>
          <p style={{ fontSize: '0.8rem', color: '#94a3b8', margin: '5px 0 0 0' }}>Nodo activo: Aragua, Venezuela | Iris, Cerebras y Vega sincronizados.</p>
        </div>
        <div style={{ fontSize: '0.8rem', background: '#0f172a', padding: '0.5rem 1rem', borderRadius: '8px', border: '1px solid #38bdf8', color: '#4ade80' }}>
          ⚡ Estado: Sistema Operativo
        </div>
      </header>

      {/* Grid Principal */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr', gap: '1.5rem' }}>
        
        {/* Panel Izquierdo: Avatar de Remi (remi_la_bonita.png) y Telemetría */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '12px', border: '1px solid #1e293b', textAlign: 'center', boxShadow: '0 4px 12px rgba(0,0,0,0.5)' }}>
            <h3 style={{ color: '#38bdf8', marginBottom: '0.8rem', fontSize: '1rem' }}>👁️ Núcleo Visual & Identidad</h3>
            <div style={{ borderRadius: '8px', overflow: 'hidden', border: '1px solid #334155' }}>
              <img 
                src="/remi_la_bonita.png" 
                alt="REMI Core Avatar" 
                style={{ width: '100%', height: 'auto', display: 'block', objectFit: 'cover' }}
              />
            </div>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.6rem' }}>Matriz de Percepción Óptica y Enlace TIGER_DATA activos.</p>
          </div>

          <div style={{ background: '#0f172a', padding: '1.2rem', borderRadius: '12px', border: '1px solid #1e293b' }}>
            <h3 style={{ color: '#38bdf8', marginBottom: '0.8rem', fontSize: '1rem' }}>⚡ Telemetría del Búnker</h3>
            <ul style={{ listStyle: 'none', padding: 0, fontSize: '0.85rem', lineHeight: '1.8' }}>
              <li>🧠 Cerebras (Razonamiento): <strong style={{ color: '#4ade80' }}>Activo</strong></li>
              <li>👁️ Argus / Iris (Visión): <strong style={{ color: '#4ade80' }}>Activo</strong></li>
              <li>🔊 Vega (TTS Audio): <strong style={{ color: modoAudioVega ? '#4ade80' : '#f87171' }}>{modoAudioVega ? 'Activo' : 'Silenciado'}</strong></li>
              <li>📂 Archivos (sda7/sda5): <strong style={{ color: '#4ade80' }}>Activo</strong></li>
            </ul>
          </div>
        </div>

        {/* Panel Derecho: Chat y Sentidos */}
        <div style={{ background: '#0f172a', padding: '1.2rem', borderRadius: '12px', border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', height: '680px' }}>
          <h3 style={{ color: '#38bdf8', marginBottom: '0.8rem', fontSize: '1rem' }}>💬 Canal de Comunicación Directa</h3>

          {/* Historial de Chat */}
          <div style={{ flex: 1, overflowY: 'auto', background: '#020617', padding: '1rem', borderRadius: '8px', marginBottom: '0.8rem', border: '1px solid #1e293b', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {chats.map((chat, idx) => (
              <div key={idx} style={{
                alignSelf: chat.remite === 'usuario' ? 'flex-end' : 'flex-start',
                background: chat.remite === 'usuario' ? '#0369a1' : '#1e293b',
                color: '#f8fafc',
                padding: '0.9rem 1.1rem',
                borderRadius: '10px',
                maxWidth: '85%',
                lineHeight: '1.5',
                fontSize: '0.9rem',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
                whiteSpace: 'pre-wrap'
              }}>
                <strong style={{ display: 'block', fontSize: '0.7rem', color: '#94a3b8', marginBottom: '0.2rem' }}>
                  {chat.remite === 'usuario' ? 'RAMÓN' : 'REMI (IA)'}
                </strong>
                {chat.imagen && (
                  <div style={{ marginBottom: '0.5rem', borderRadius: '6px', overflow: 'hidden', border: '1px solid #38bdf8' }}>
                    <img src={chat.imagen} alt="Preview" style={{ width: '100%', maxHeight: '200px', objectFit: 'contain', display: 'block', background: '#000' }} />
                  </div>
                )}
                {chat.texto}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          {/* Panel flotante de previsualización de imagen adjunta antes de enviar */}
          {imagenBase64 && (
            <div style={{ background: '#0f2922', border: '1px solid #059669', padding: '0.6rem', borderRadius: '8px', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                <img src={imagenBase64} alt="Miniatura" style={{ width: '45px', height: '45px', objectFit: 'cover', borderRadius: '4px', border: '1px solid #34d399' }} />
                <span style={{ fontSize: '0.8rem', color: '#34d399' }}>📎 Listo para Iris: <strong>{nombreArchivo}</strong></span>
              </div>
              <button onClick={() => { setImagenBase64(null); setNombreArchivo(''); }} style={{ background: 'transparent', border: 'none', color: '#fff', cursor: 'pointer', fontWeight: 'bold', fontSize: '1rem' }}>✕</button>
            </div>
          )}

          {/* Menú de Opciones y Sentidos desplegable */}
          {menuAbierto && (
            <div style={{ background: '#1e293b', padding: '0.8rem', borderRadius: '8px', marginBottom: '0.8rem', display: 'flex', gap: '0.8rem', border: '1px solid #334155', zIndex: 10 }}>
              <label style={{ background: '#0f172a', color: '#38bdf8', border: '1px solid #475569', padding: '0.4rem 0.7rem', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.8rem' }}>
                📎 Adjuntar Imagen / Archivo
                <input 
                  type="file" 
                  ref={fileInputRef}
                  accept="image/*"
                  style={{ display: 'none' }} 
                  onChange={handleFileChange} 
                />
              </label>
              <button 
                onClick={toggleMic} 
                style={{ background: '#0f172a', color: escuchandoVoz ? '#f43f5e' : '#4ade80', border: '1px solid #475569', padding: '0.4rem 0.7rem', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem' }}
              >
                🎤 Micrófono ({escuchandoVoz ? 'ON' : 'OFF'})
              </button>
              <button 
                onClick={toggleEscucharRespuesta} 
                style={{ background: '#0f172a', color: modoAudioVega ? '#4ade80' : '#94a3b8', border: '1px solid #475569', padding: '0.4rem 0.7rem', borderRadius: '6px', cursor: 'pointer', fontSize: '0.8rem' }}
              >
                🔊 Voz Vega ({modoAudioVega ? 'ON' : 'OFF'})
              </button>
            </div>
          )}

          {/* Área de Entrada y Botones */}
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <button 
              onClick={() => setMenuAbierto(!menuAbierto)}
              style={{ background: '#1e293b', border: '1px solid #475569', color: '#38bdf8', padding: '0.7rem 0.9rem', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '1rem' }}
              title="Menú de Sentidos (Iris / Vega)"
            >
              ➕
            </button>

            <textarea
              rows="1"
              style={{ flex: 1, padding: '0.7rem', background: '#020617', color: '#f8fafc', border: '1px solid #334155', borderRadius: '8px', resize: 'none', outline: 'none', fontSize: '0.9rem' }}
              value={mensaje}
              onChange={(e) => setMensaje(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); enviar(); }}}
              placeholder={escuchandoVoz ? "Escuchando voz..." : "Escribe tu instrucción o adjunta una imagen..."}
            />

            <button 
              onClick={enviar}
              disabled={loading}
              style={{ background: '#0284c7', color: '#fff', border: 'none', padding: '0.7rem 1.2rem', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', fontSize: '0.9rem' }}
            >
              {loading ? '...' : 'Enviar'}
            </button>
          </div>
        </div>

      </div>
    </main>
  );
}
