import { createWalletClient, createPublicClient, http, stringToHex, getAddress, defineChain } from "viem";
import { privateKeyToAccount } from "viem/accounts";

const hardhatChain = defineChain({
  id: 31337,
  name: 'Hardhat',
  network: 'hardhat',
  nativeCurrency: { decimals: 18, name: 'Ether', symbol: 'ETH' },
  rpcUrls: { default: { http: ['http://127.0.0.1:8545'] }, public: { http: ['http://127.0.0.1:8545'] } },
});

async function main() {
  const hashReal = "4a5bceca462fd3d4cf86657d4d9969a677701ba60b816c69c1678e7b35f9b487";
  const account = privateKeyToAccount("0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80");
  const target = getAddress("0x70997970C51812dc3A010C7d01b50e0d17dc79C8");

  const client = createWalletClient({ account, chain: hardhatChain, transport: http() });
  const publicClient = createPublicClient({ chain: hardhatChain, transport: http() });

  console.log("🚀 EJECUTANDO SELLADO DEFINITIVO EN CHAIN 31337...");

  const hashTx = await client.sendTransaction({
    to: target,
    data: stringToHex("REMI_GENESIS_SEAL_" + hashReal)
  });

  const receipt = await publicClient.waitForTransactionReceipt({ hash: hashTx });

  console.log("\n💎 ¡BÚNKER SELLADO DE FORMA INMUTABLE! 💎");
  console.log("🔗 TX HASH REAL: " + hashTx);
  console.log("📊 BLOQUE NÚMERO: " + receipt.blockNumber);
}

main().catch(console.error);
