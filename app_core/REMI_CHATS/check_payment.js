import { ethers } from "ethers";

async function main() {
    // Conexión directa al puerto del nodo
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    
    // La dirección que desplegaste antes del descanso
    const contratoDireccion = "NUEVA_DIRECCION";

    // ABI manual: Sin archivos, sin errores de lectura. Solo la firma de la función.
    const abi = ["function getPrecioConsulta() public view returns (uint256)"];

    const contrato = new ethers.Contract(contratoDireccion, abi, provider);

    try {
        console.log("----------------------------------------------");
        console.log("SONDEANDO CONTRATO: " + contratoDireccion);
        
        // Llamada directa al nodo
        const precioWei = await contrato.getPrecioConsulta();
        const precioEth = ethers.formatEther(precioWei);
        
        console.log("ESTADO: ¡LECTURA EXITOSA!");
        console.log("PRECIO DETECTADO: " + precioEth + " ETH");
        console.log("----------------------------------------------");
    } catch (error) {
        console.log("----------------------------------------------");
        console.log("ERROR DE CONEXIÓN O DIRECCIÓN INEXISTENTE.");
        console.log("Causa probable: El nodo se reinició y el contrato se borró.");
        console.log("----------------------------------------------");
    }
}
main();
