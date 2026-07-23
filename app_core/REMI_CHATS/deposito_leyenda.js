const { ethers } = require("ethers");

async function inyeccionMasiva() {
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    const accounts = await provider.listAccounts();
    const signer = await provider.getSigner(accounts[0].address);
    
    // 99 ETH es seguro porque la cuenta tiene 100
    const cantidad = "99.0"; 
    
    try {
        const tx = await signer.sendTransaction({
            to: "0x96De980a766CCb10A19B6962587e2b61B650b372",
            value: ethers.parseEther(cantidad)
        });
        
        console.log(`🚀 Iniciando transferencia de ${cantidad} ETH...`);
        await tx.wait();
        console.log("✅ Capitalización completada. El Búnker ahora tiene peso institucional.");
    } catch (error) {
        console.log("❌ Error:", error.message);
    }
}

inyeccionMasiva();
