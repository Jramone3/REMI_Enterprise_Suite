// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title PatrimonioREMI v2.0
 * @dev Notario digital inmutable para auditorías de Remi Finance.
 * Solo el dueño (Búnker) puede sellar registros.
 */
contract PatrimonioREMI {
    address public owner;
    
    struct Registro {
        string hashSDA5;      // Hash de la evidencia (Informe/PoC)
        uint256 timestamp;    // Marca de tiempo inmutable
        string custodio;      // Identificador del módulo Remi
    }

    mapping(uint256 => Registro) public bloques;
    uint256 public contadorBloques;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Acceso denegado: Solo el Bunker Owner puede sellar.");
        _;
    }

    function sellarPatrimonio(string memory _hash, string memory _custodio) public onlyOwner {
        contadorBloques++;
        bloques[contadorBloques] = Registro(_hash, block.timestamp, _custodio);
    }
}
