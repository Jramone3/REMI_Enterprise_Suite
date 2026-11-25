export const metadata = {
  title: 'REMI Centro de Mando',
  description: 'Autonomous AI Agent Core & AuthBridge',
}

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        {children}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.speakRemi = function(text) {
                if ('speechSynthesis' in window && text) {
                  window.speechSynthesis.cancel();
                  const utterance = new SpeechSynthesisUtterance(text);
                  utterance.lang = 'es-ES';
                  utterance.pitch = 1.2;
                  utterance.rate = 1.0;
                  window.speechSynthesis.speak(utterance);
                }
              };

              const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                  mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.innerText) {
                      const text = node.innerText.trim();
                      if (text.length > 25 && (text.includes("REMI") || text.includes("Ramón")) && !node.dataset.voiced) {
                        node.dataset.voiced = "true";
                        window.speakRemi(text.substring(0, 150));
                      }
                    }
                  });
                });
              });

              window.addEventListener('DOMContentLoaded', () => {
                observer.observe(document.body, { childList: true, subtree: true });
                console.log("[*] Vega TTS Autonomous Bridge Activo en Puerto 3000.");
              });
            `,
          }}
        />
      </body>
    </html>
  )
}
