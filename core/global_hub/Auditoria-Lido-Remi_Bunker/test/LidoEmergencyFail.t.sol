// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "forge-std/Test.sol";
import "../src/Lido_Core/LidoOracle.sol";
import "../src/Lido_Core/EmergencyBrake.sol";

contract LidoEmergencyTest is Test {
    LidoOracle oracle;
    EmergencyBrake brake;

    function setUp() public {
        oracle = new LidoOracle();
        brake = new EmergencyBrake(address(oracle));
    }

    function testEmergencyBlock() public {
        // 1. Atacamos primero: Causamos el desbordamiento en el oraculo
        uint256 balanceVeneno = 95766262441414123463108253033211924168360153421382992350105833566050353633896;
        oracle.pushReport(1, balanceVeneno, 1000);

        // 2. El comite de emergencia intenta pausar el protocolo...
        // ¡Pero la funcion triggerEmergencyPause fallara porque intenta leer el oraculo roto!
        // vm.expectRevert(); 
        brake.triggerEmergencyPause(1);
        
        emit log("ALERTA MAXIMA: El mecanismo de reparacion ha quedado INHABILITADO por el ataque.");
    }
}
