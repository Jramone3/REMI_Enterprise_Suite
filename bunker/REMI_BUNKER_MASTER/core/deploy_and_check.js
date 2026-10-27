import pkg from 'hardhat';
const { ethers } = pkg;

async function main() {
    console.log("Compilación de Hardhat completada. Iniciando verificación/despliegue...");
    
    // Aquí puedes colocar la lógica de ethers que necesites probar, por ejemplo:
    const [deployer] = await ethers.getSigners();
    console.log("Desplegando con la cuenta:", deployer.address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
