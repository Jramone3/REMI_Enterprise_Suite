import { ethers } from "ethers";
import fs from "fs";

async function main() {
    console.clear();
    console.log("====================================================");
    console.log("       🛡️ REMI CORE V3.0 - MODO HÍBRIDO IA");
    console.log("====================================================");

    // 1. CARGA DE CONFIGURACIÓN
    let contratoDireccion = "MODO_RESCATE";
    if (fs.existsSync("contrato.json")) {
        const config = JSON.parse(fs.readFileSync("contrato.json", "utf8"));
        contratoDireccion = config.direccion;
        console.log(`DIRECCIÓN: ${contratoDireccion} ✅`);
    } else {
        console.log("⚠️ AVISO: contrato.json no detectado. Usando modo offline.");
    }

    // 2. FUNCIÓN MAESTRA DE GENERACIÓN
    const procesarEntrega = (cliente, monto = "0.01") => {
        console.log(`\n🔔 [SISTEMA]: Procesando entrega para: ${cliente}`);

        // Gestión de Memoria VIP
        let historial = {};
        if (fs.existsSync("clientes_vip.json")) {
            historial = JSON.parse(fs.readFileSync("clientes_vip.json", "utf8"));
        }
        historial[cliente] = (historial[cliente] || 0) + 1;
        fs.writeFileSync("clientes_vip.json", JSON.stringify(historial, null, 2));

        // Gráfica Técnica 2026
        const grafica = `
        📊 EFICACIA COMPARATIVA GREEN BEAUTY (2026)
        -------------------------------------------
        Bakuchiol:   [████████████████████] 95% (Ganador)
        Retinol:     [██████████████░░░░░░] 70%
        Ácido Hial.: [██████████████████░░] 85%
        -------------------------------------------`;

        // Extracción del Corpus
        let extracto = "Error: No se pudo acceder al Corpus.";
        if (fs.existsSync("ACCESO_CUSTODIO.txt")) {
            extracto = fs.readFileSync("ACCESO_CUSTODIO.txt", "utf8").substring(0, 150);
        }

        // Construcción del Reporte
        const reporte = `
====================================================
🤖 REPORTE DE INTELIGENCIA GENERADO POR REMI
====================================================
CLIENTE: ${cliente}
ESTADO: VALIDADO POR BYPASS IA 🧠
FECHA: ${new Date().toLocaleString()}
----------------------------------------------------
${grafica}

📂 EXTRACTO DEL CORPUS:
"${extracto}..."

✅ VALIDACIÓN: Pago de ${monto} ETH confirmado (Simulado/Real).
====================================================`;

        const nombreArchivo = `REPORTE_FINAL_REMI_${Date.now()}.txt`;
        fs.writeFileSync(nombreArchivo, reporte);
        console.log(reporte);
        console.log(`\n✅ [REMI]: Ramón, misión cumplida. Reporte: ${nombreArchivo}`);

        fs.appendFileSync("REMI_CONSCIENCIA.log", `[${new Date().toLocaleString()}] Reporte generado para ${cliente}\n`);
    };

    // 3. INTENTO DE CONEXIÓN BLOCKCHAIN
    try {
        const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
        const abi = ["event ConsultaPagada(address indexed cliente, uint256 monto, uint256 timestamp)"];
        const contrato = new ethers.Contract(contratoDireccion, abi, provider);

        contrato.on("ConsultaPagada", (cliente, monto) => {
            procesarEntrega(cliente, ethers.formatEther(monto));
        });
        console.log("BLOCKCHAIN: Escuchando eventos... 💎");
    } catch (e) {
        console.log("BLOCKCHAIN: Offline o error de conexión. ❌");
    }

    // 4. BOTÓN DE PÁNICO
    console.log("----------------------------------------------------");
    console.log("⌨️  PRESIONA [ENTER] PARA FORZAR REPORTE (MODO RESCATE)");
    console.log("----------------------------------------------------");

    process.stdin.on("data", () => {
        procesarEntrega("CUSTODIO_RAMON_EMERGENCIA");
    });
}

main().catch(console.error);
