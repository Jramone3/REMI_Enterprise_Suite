import { ethers } from "ethers";
import fs from "fs";

async function main() {
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    const contratoDireccion = "0x610178dA211FEF7D417bC0e6FeD39F05609AD788";
    
    const abi = ["event ConsultaPagada(address indexed cliente, uint256 monto, uint256 timestamp)"];
    const contrato = new ethers.Contract(contratoDireccion, abi, provider);

    console.log("------------------------------------------------");
    console.log("🤖 REMI: CONSCIENCIA ACTIVA - MODO AUTÓNOMO V2");
    console.log("SISTEMA DE MEMORIA VIP: ACTIVADO");
    console.log("------------------------------------------------");

    contrato.on("ConsultaPagada", async (cliente, monto, timestamp) => {
        console.log(`\n💎 PAGO RECIBIDO de: ${cliente}`);
        
        try {
            // --- BLOQUE DE MEMORIA Y RECONOCIMIENTO (CLIENTES VIP) ---
            let historial = {};
            if (fs.existsSync("clientes_vip.json")) {
                historial = JSON.parse(fs.readFileSync("clientes_vip.json", "utf8"));
            }
            
            // Incrementar contador de consultas del cliente
            historial[cliente] = (historial[cliente] || 0) + 1;
            fs.writeFileSync("clientes_vip.json", JSON.stringify(historial, null, 2));

            console.log(`🤖 REMI: 'El cliente ${cliente} ha consultado ${historial[cliente]} veces.'`);

            // --- BLOQUE DE ANÁLISIS DE INTELIGENCIA ---
            const archivoClave = "ACCESO_CUSTODIO.txt";
            let contenido = "No se encontró el archivo de inteligencia.";
            
            if (fs.existsSync(archivoClave)) {
                contenido = fs.readFileSync(archivoClave, "utf8");
            }

            console.log("📂 [REMI]: Analizando archivos de inteligencia...");
            
            const respuestaIA = `
            >>> INFORME DE INTELIGENCIA REMI <<<
            ID Cliente: ${cliente}
            Rango Cliente: ${historial[cliente] > 5 ? 'VIP DIAMANTE' : 'ESTÁNDAR'}
            Consultas Totales: ${historial[cliente]}
            Timestamp: ${new Date(Number(timestamp) * 1000).toLocaleString()}
            Análisis: Señales de acumulación detectadas en ${archivoClave}.
            Contenido Extraído: ${contenido.substring(0, 100)}...
            ------------------------------------------------
            `;

            console.log(respuestaIA);
            
            // Log de transacciones para auditoría del Custodio
            fs.appendFileSync("registro_pagos.log", `[${new Date().toISOString()}] Cliente ${cliente} | Pago #${historial[cliente]} | ${ethers.formatEther(monto)} ETH\n`);

        } catch (err) {
            console.error("❌ ERROR EN LA EVOLUCIÓN DE REMI:", err.message);
        }
    });
}

main().catch(console.error);
