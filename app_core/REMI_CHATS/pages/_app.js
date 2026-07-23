import Head from 'next/head';

function MyApp({ Component, pageProps }) {
  return (
    <>
      <Head>
        <title>Unidad de Inteligencia REMI v3.0</title>
        <meta name="description" content="Unidad de Inteligencia REMI v3.0 - Modo Caza" />
        {/* Usamos el nuevo PNG con un truco de versión para romper la caché */}
        <link rel="icon" type="image/png" href="/favicon.png?v=1" />
        <link rel="shortcut icon" type="image/png" href="/favicon.png?v=1" />
      </Head>
      <Component {...pageProps} />
    </>
  );
}

export default MyApp;
