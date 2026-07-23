// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PatrimonioREMI {
    struct Registro {
        string hashSDA5;
        uint256 timestamp;
        string custodio;
    }

    mapping(uint256 => Registro) public bloques;
    uint256 public contadorBloques;

    function sellarPatrimonio(string memory _hash, string memory _custodio) public {
        contadorBloques++;
        bloques[contadorBloques] = Registro(_hash, block.timestamp, _custodio);
    }
}
