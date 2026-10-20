/**
 * REMI Enterprise Suite - Frontend Gateway Adapter
 * Robust HTTP client bridge targeting backend port 5000.
 */

const BACKEND_ENDPOINT = "http://localhost:5000/api/remi";

async function dispatchUserQuery(userMessage, speakAudio = true) {
    try {
        const payload = {
            message: userMessage,
            speak: speakAudio,
            lang: "es"
        };

        const response = await fetch(BACKEND_ENDPOINT, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`HTTP network error status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("[FRONTEND_BRIDGE_ERROR]: Pipeline execution failed ->", error);
        return {
            status: "FAILURE",
            message: "Error de conexión con el núcleo soberano."
        };
    }
}

module.exports = { dispatchUserQuery };
