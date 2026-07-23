import hre from "hardhat";
import { parseEther } from "viem";

async function main() {
  const hashReal = "4a5bceca462fd3d4cf86657d4d9969a677701ba60b816c69c1678e7b35f9b487";
  
  // En Viem para Hardhat 3 se accede así:
  const [deployer] = await hre.viem.getWalletClients();
  const publicClient = await hre.viem.getPublicClient();
  
  console.log("🚀 Iniciando Sellado REAL con la cuenta:", deployer.account.address);
  console.log("📦 Hash de Integridad Detectado:", hashReal);

  // Enviamos la transacción para registrar el hash en el histórico de la red
  const hashTx = await deployer.sendTransaction({
    to: "0x96De980a766CCb10A19B6962587e2b61B650b372",
    value: 0n,
    data: "0x" + Buffer.from("REMI_GENESIS_SEAL_" + hashReal).toString('hex')
  });

  console.log("⏳ Esperando confirmación del bloque...");
  await publicClient.waitForTransactionReceipt({ hash: hashTx });

  console.log("✅ ¡EL BÚNKER HA SIDO SELLADO EN LA BLOCKCHAIN!");
  console.log("🔗 ID de Transacción (TX HASH):", hashTx);
}

main().catch((error) => {
  console.error("❌ ERROR TÉCNICO:", error);
  process.exit(1);
});
