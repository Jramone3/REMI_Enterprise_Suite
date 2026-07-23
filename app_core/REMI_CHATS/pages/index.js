import Layout from './layout';
import Link from 'next/link';

export default function Home() {
  const linkStyle = { 
    color: '#fff', 
    textDecoration: 'none', 
    textShadow: '2px 2px 4px #000',
    fontSize: '1.2rem'
  };

  return (
    <Layout>
      <h1 style={{ color: '#d4af37', textShadow: '2px 2px 4px #000' }}>
        🚀 Consola REMI
      </h1>

      <section style={{ marginTop: '2rem' }}>
        <ul style={{ listStyle: 'none', paddingLeft: 0, lineHeight: '2.5' }}>
          <li>📂 <Link href="/projects" style={linkStyle}>Projects · Espacio de Trabajo</Link></li>
          <li>📊 <Link href="/monitor" style={linkStyle}>Monitor de Visualización</Link></li>
          <li>📘 <Link href="/bitacora" style={linkStyle}>Bitácora de Eventos</Link></li>
          <li>📦 <Link href="/exportador" style={linkStyle}>Exportador CSV</Link></li>
          <li>🧪 <Link href="/comparador" style={linkStyle}>Comparador de Huellas SHA256</Link></li>
          <li>📜 <Link href="/publicador" style={linkStyle}>Publicador y Verificador</Link></li>
          <li>💬 <Link href="/chat" style={linkStyle}>Ir al Chat</Link></li>
          <li>🧭 <Link href="/estado" style={linkStyle}>Estado del Sistema</Link></li>
        </ul>
      </section>
    </Layout>
  );
}
