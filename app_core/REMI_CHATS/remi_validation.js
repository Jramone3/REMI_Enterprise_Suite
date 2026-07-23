import { ethers } from "ethers";
import fs from "fs";

async function main() {
    const config = JSON.parse(fs.readFileSync("contrato.json", "utf8"));
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    const cuentas = await provider.listAccounts();
    const cliente = await provider.getSigner(cuentas[1].address);

    console.log(`💸 Enviando 0.01 ETH a: ${config.direccion}`);

    const tx = await cliente.sendTransaction({
        to: config.direccion,
        value: ethers.parseEther("0.01"),
        gasLimit: 50000n
    });

    await tx.wait();
    console.log("🔓 ¡LOGRADO! Pago aceptado por la red.");
}
main().catch(console.error);
