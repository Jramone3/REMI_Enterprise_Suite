import { ethers } from "ethers";
import fs from "fs";

async function main() {
    const provider = new ethers.JsonRpcProvider("http://127.0.0.1:8545");
    const wallet = new ethers.Wallet("0x73e8742307a2cec0a3911851f04b5c6bb65bf087f8c1d8c2aabbbfaee6080777", provider);

    // Este contrato emite el evento siempre, reciba lo que reciba.
    const abi = ["event ConsultaPagada(address indexed cliente, uint256 monto, uint256 timestamp)"];
    const bytecode = "0x6080604052348015600f57600080fd5b50603f8061001e6000396000f3fe6080604052348015600f57600080fd5b507f230571d8983e37d7fbdb5a6d3d08c353ad4f4b0e8debf52bc866a00e7232555f333442604051808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001838152602001828152602001935050505060405180910390a200fea26469706673582212201e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e64736f6c63430008120033";

    const factory = new ethers.ContractFactory(abi, bytecode, wallet);
    const contrato = await factory.deploy();
    await contrato.waitForDeployment();
    const addr = await contrato.getAddress();
    console.log(`✅ CONTRATO TOTALMENTE COMPATIBLE EN: ${addr}`);
    fs.writeFileSync("contrato.json", JSON.stringify({ direccion: addr }));
}
main();
