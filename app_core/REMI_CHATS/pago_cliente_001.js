const { ethers } = require("ethers");

async function simularPagoCliente() {
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    const accounts = await provider.listAccounts();
    // Usamos la cuenta #2 de Ganache como si fuera un cliente externo
    const clienteSigner = await provider.getSigner(accounts[2].address); 
    
    const monto = "0.5";
    console.log(`\n📦 [CLIENTE_EXTERNO]: Iniciando pago de ${monto} ETH por servicios de Búnker...`);

    const tx = await clienteSigner.sendTransaction({
        to: "0x96De980a766CCb10A19B6962587e2b61B650b372",
        value: ethers.parseEther(monto)
    });

    await tx.wait();
    console.log(`✅ [BLOCKCHAIN]: Transacción confirmada. Hash: ${tx.hash}`);
}

simularPagoCliente();
