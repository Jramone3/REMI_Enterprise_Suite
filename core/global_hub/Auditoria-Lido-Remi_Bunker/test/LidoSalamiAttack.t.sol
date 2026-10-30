// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "forge-std/Test.sol";
import "../src/Lido_Core/SanityChecker.sol";

contract LidoSalamiTest is Test {
    SanityChecker guardian;

    function setUp() public {
        guardian = new SanityChecker();
    }

    function testSalamiTactics() public {
        uint256 balanceInicial = 100 ether;
        uint256 balanceActual = balanceInicial;
        
        emit log("--- Iniciando Ataque Salami (Multi-Etapa) ---");

        for(uint i = 1; i <= 5; i++) {
            uint256 nuevoBalance = (balanceActual * 10900) / 10000;
            bool esSeguro = guardian.isReportSafe(nuevoBalance, balanceActual);
            
            emit log_named_uint("Paso", i);
            emit log_named_uint("Nuevo Balance (ether)", nuevoBalance / 1e18);
            
            if (esSeguro) {
                emit log("Estado: Reporte aceptado por el Guardian");
            } else {
                emit log("Estado: Reporte RECHAZADO");
            }
            
            balanceActual = nuevoBalance;
        }

        uint256 inflacionTotal = (balanceActual * 100) / balanceInicial;
        emit log_named_uint("Inflacion Total Acumulada (%)", inflacionTotal);
        
        if (inflacionTotal > 150) {
            emit log("ALERTA CRITICA: El Guardian permitio una inflacion del 50 por ciento en 5 pasos.");
        }
    }
}
