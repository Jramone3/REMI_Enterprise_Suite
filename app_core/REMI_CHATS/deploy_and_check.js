import { ethers } from "ethers";
import fs from "fs";

async function main() {
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    const wallet = new ethers.Wallet("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80", provider);

    console.log("----------------------------------------------");
    const artifactPath = "./artifacts/contracts/PrediccionMercado.sol/PrediccionMercado.json";
    const artifact = JSON.parse(fs.readFileSync(artifactPath, "utf8"));

    const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode, wallet);
    console.log("Desplegando contrato corregido...");
    const contrato = await factory.deploy();
    await contrato.waitForDeployment();
    
    const direccion = await contrato.getAddress();

    try {
        // LLAMADA CORRECTA AL NOMBRE DE LA VARIABLE PÚBLICA
        const precioWei = await contrato.precioConsulta(); 
        const precioEth = ethers.formatEther(precioWei);
        
        console.log("¡ÉXITO CUÁNTICO!");
        console.log("CONTRATO: " + direccion);
        console.log("PRECIO ACTUAL: " + precioEth + " ETH");
        console.log("----------------------------------------------");
    } catch (error) {
        console.log("ERROR: " + error.message);
    }
}
main().catch(console.error);
