// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract RNC_Notary_Immunefi {
    address public immutable owner;
    string public constant nombreContrato = "REMI-NOTARY-CORE-01";
    
    struct Auditoria {
        string protocolo;
        string hashHallazgo;
        uint256 timestamp;
    }

    // PRIVADO: Solo el dueño puede leer la bitácora
    mapping(uint256 => Auditoria) private bitacora;
    uint256 public contadorHallazgos;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Acceso denegado: Solo el Custodio");
        _;
    }

    // Función de registro
    function registrarHallazgo(string memory _protocolo, string memory _hash) public onlyOwner {
        contadorHallazgos++;
        bitacora[contadorHallazgos] = Auditoria(_protocolo, _hash, block.timestamp);
    }

    // CONSULTA SEGURA: Solo el dueño puede ver los datos
    function consultarHallazgo(uint256 _id) public view onlyOwner returns (string memory, string memory, uint256) {
        Auditoria memory a = bitacora[_id];
        return (a.protocolo, a.hashHallazgo, a.timestamp);
    }
}
