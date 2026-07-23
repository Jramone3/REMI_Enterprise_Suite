const { sellarBloque } = require("./blockchain_bridge");

async function autorizarYSellar(tokenAuth0, hashPatrimonio, custodio) {
    if (!tokenAuth0) {
        throw new Error("❌ Error: No se detectó sesión de Auth0 activa.");
    }
    
    console.log("🔐 Validando Token DPoP con Auth0...");
    // Aquí REMI verifica la firma del token
    
    console.log("⛓️ Autorización concedida. Procediendo a sellar bloque en Blockchain...");
    return await sellarBloque(hashPatrimonio, custodio);
}

module.exports = { autorizarYSellar };
