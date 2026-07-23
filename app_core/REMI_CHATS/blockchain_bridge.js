const { ethers } = require("ethers");

const CONTRACT_ABI = [
    "function sellarPatrimonio(string memory _hash, string memory _custodio) public",
    "function contadorBloques() public view returns (uint256)",
    "function bloques(uint256) public view returns (string memory hashSDA5, uint256 timestamp, string memory custodio)"
];

const CONTRACT_BYTECODE = "0x6080604052348015600e575f5ffd5b506108c78061001c5f395ff3fe608060405234801561000f575f5ffd5b506004361061003f575f3560e01c8063872eb70a14610043578063ecd824421461005f578063ef59bb391461007d575b5f5ffd5b61005d600480360381019061005891906103b2565b6100af565b005b61006761012e565b6040516100749190610440565b60405180910390f35b61009760048036038101906100929190610483565b610134565b6040516100a69392919061050e565b60405180910390f3";

async function iniciarContrato(signer) {
    try {
        console.log("🛠 Iniciando despliegue de contrato...");
        const factory = new ethers.ContractFactory(CONTRACT_ABI, CONTRACT_BYTECODE, signer);
        const contract = await factory.deploy();
        await contract.waitForDeployment();
        const addr = await contract.getAddress();
        console.log("🚀 Contrato PatrimonioREMI desplegado en:", addr);
        return contract;
    } catch (error) {
        console.error("❌ Error al desplegar contrato:", error);
        throw error;
    }
}

// Exportación segura
module.exports = { CONTRACT_ABI, CONTRACT_BYTECODE, iniciarContrato };
