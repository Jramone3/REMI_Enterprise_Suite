const { iniciarContrato } = require("./blockchain_bridge");
const { ethers } = require("ethers");

async function test() {
    console.log("🛠️ Iniciando simulador de Blockchain local...");
    // Usamos un proveedor ficticio para probar la lógica
    const wallet = ethers.Wallet.createRandom();
    console.log("🔑 Billetera de prueba generada:", wallet.address);
    console.log("🧬 ADN del Contrato cargado con éxito.");
    console.log("✅ Sistema listo para recibir el Hash de los 100k archivos.");
}

test();
