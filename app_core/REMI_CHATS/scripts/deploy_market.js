import { ethers } from "ethers";
import fs from "fs";

async function main() {
    // Conexión manual al nodo de la Terminal 5
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    
    // Usamos la clave privada de la Cuenta #0 de Hardhat para firmar
    const wallet = new ethers.Wallet("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80", provider);

    console.log("----------------------------------------------");
    console.log("DESPLEGANDO DESDE CUENTA:", wallet.address);

    const artifactPath = "./artifacts/contracts/PrediccionMercado.sol/PrediccionMercado.json";
    if (!fs.existsSync(artifactPath)) {
        console.error("ERROR: No encuentro el contrato compilado. ¿Ejecutaste npx hardhat compile?");
        return;
    }

    const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));
    const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, wallet);

    console.log("Enviando contrato al nodo local...");
    const contract = await factory.deploy();
    await contract.waitForDeployment();

    const address = await contract.getAddress();
    console.log("¡ÉXITO TOTAL!");
    console.log("DIRECCIÓN REAL DEL CONTRATO:", address);
    console.log("----------------------------------------------");
}

main().catch((error) => {
    console.error("Fallo en el despliegue:", error);
});
