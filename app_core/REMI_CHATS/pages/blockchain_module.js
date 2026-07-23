import { useState } from 'react';

export default function BlockchainModule() {
  const [status, setStatus] = useState('Esperando Autorización Auth0...');

  return (
    <div style={{ padding: '20px', border: '1px solid #FFD700', borderRadius: '10px', backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <h3 style={{ color: '#FFD700' }}>🔒 Nodo Blockchain REMI</h3>
      <p style={{ color: '#00FBFF' }}>Estado: {status}</p>
      <button 
        onClick={() => setStatus('Sellando bloque con Auth0 DPoP...')}
        style={{
          backgroundColor: '#FF4500',
          color: 'white',
          border: 'none',
          padding: '10px 20px',
          cursor: 'pointer',
          fontWeight: 'bold',
          borderRadius: '5px'
        }}
      >
        FIRMAR PATRIMONIO (100K FILES)
      </button>
    </div>
  );
}
