const hre = require("hardhat");

async function main() {
  const PrediccionMercado = await hre.ethers.getContractFactory("PrediccionMercado");
  const contrato = await PrediccionMercado.deploy();

  await contrato.waitForDeployment();

  console.log("----------------------------------------------");
  console.log("CONTRATO DE MONETIZACIÓN DESPLEGADO");
  console.log("Dirección del Contrato:", await contrato.getAddress());
  console.log("Dueño del Búnker (Custodio):", await contrato.owner());
  console.log("----------------------------------------------");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
