const { ethers } = require("ethers");

async function depositar() {
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    const accounts = await provider.listAccounts();
    const signer = await provider.getSigner(accounts[0].address); // La cuenta #0 le paga a Ramón
    
    const tx = await signer.sendTransaction({
        to: "0x96De980a766CCb10A19B6962587e2b61B650b372",
        value: ethers.parseEther("1.0")
    });
    
    console.log("🚀 Enviando 1.0 ETH al búnker...");
    await tx.wait();
    console.log("✅ ¡Transacción confirmada!");
    console.log("Hash:", tx.hash);
}

depositar();
