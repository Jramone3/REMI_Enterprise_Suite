export default function Layout({ children }) {
  return (
    <div style={{
      backgroundColor: '#000',
      backgroundImage: 'url("/imagen_visual_remi.png")',
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundAttachment: 'fixed',
      minHeight: '100vh',
      color: '#00FBFF', // Cian Neón para todo el texto
      fontFamily: 'monospace'
    }}>
      <div style={{ 
        backgroundColor: 'rgba(0, 0, 0, 0.4)', 
        minHeight: '100vh', 
        padding: '20px',
        backdropFilter: 'blur(1.5px)'
      }}>
        <style jsx global>{`
          h1, h2, h3 { color: #FFD700 !important; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5); }
          p, span, div { color: #00FBFF; }
          strong { color: #FF4500; } /* Naranja para advertencias */
        `}</style>
        <main>{children}</main>
      </div>
    </div>
  );
}
