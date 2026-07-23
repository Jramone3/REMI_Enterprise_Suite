const { ethers } = require("ethers");

async function iniciarVigilancia() {
    // Usamos el proveedor para conectarnos al motor de Ganache
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    const direccion = "0x96De980a766CCb10A19B6962587e2b61B650b372";
    
    console.log("\n==================================================");
    console.log("🛡️  SISTEMA REMI - REPORTE PATRIMONIAL");
    console.log("==================================================\n");
    console.log(`📡 Conectado al Búnker (Puerto 8545)`);
    console.log(`🏦 Bóveda: ${direccion}\n`);

    try {
        const balance = await provider.getBalance(direccion);
        const eth = ethers.formatUnits(balance, "ether");
        
        console.log("--------------------------------------------------");
        console.log(`💰 SALDO ACTUAL: ${eth} ETH`);
        console.log("--------------------------------------------------");
        
        if (parseFloat(eth) === 0) {
            console.log("⚠️  Bóveda en espera de activos.");
            console.log("💡 QR vinculado: remi.bunker.sys@proton.me");
        } else {
            console.log("🟢 ¡FONDOS VERIFICADOS!");
        }
    } catch (error) {
        console.log("❌ Error al leer la bóveda: El motor de red no responde.");
        console.log("   Asegúrate de que el nodo de Ganache sigue corriendo.");
    }
    console.log("\n==================================================");
}

iniciarVigilancia();
