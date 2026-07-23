import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox-viem";

const config = {
  solidity: "0.8.20",
  networks: {
    hardhat: {
      chainId: 31337
    }
  }
};

export default config;
