// SPDX-License-Identifier: GPL-3.0-only
pragma solidity 0.8.17;

import "forge-std/Test.sol";
import "../../src/test_isolation/RebateStaking.sol"; 
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

contract MockToken is ERC20 {
    // Recibe el 'receiver' como argumento
    constructor(address receiver) ERC20("Token", "T") { 
        _mint(receiver, 1_000_000 ether); 
    }
}

contract RebateStakingAudit is Test {
    RebateStaking target;
    MockToken token;

    function setUp() public {
        // Pasamos address(this) para que el contrato de test tenga los tokens
        token = new MockToken(address(this));
        
        // Despliega la implementación
        RebateStaking implementation = new RebateStaking();
        
        // Inicialización
        bytes memory data = abi.encodeWithSelector(
            RebateStaking.initialize.selector, 
            address(this), 
            address(token), 
            1 days, 
            7 days, 
            100
        );
        
        // Despliega el Proxy
        address proxy = address(new ERC1967Proxy(address(implementation), data));
        target = RebateStaking(proxy);

        // ¡IMPORTANTE! Aseguramos fondos para el test
        // El constructor de MockToken ya hace _mint(address(this), ...)
        // así que el contrato de test ya tiene 1,000,000 ether.
    }

   function test_ForceTransfer_Gas_Stress() public {
        address oldStaker = address(0x1);
        address newStaker = address(0x2);
        
        // 1. Dar tokens y hacer stake para que oldStaker sea válido
        token.transfer(oldStaker, 1000 ether);
        vm.startPrank(oldStaker);
        token.approve(address(target), 1000 ether);
        target.stake(1000 ether);
        vm.stopPrank();
        
        // 2. Llenamos el storage del staker original
        uint256 n = 100;
        for (uint i = 0; i < n; i++) {
            // Necesitamos que el bridge (address(this)) llame a applyForRebate
            target.applyForRebate(oldStaker, 1, RebateStaking.TreasuryFeeType.Deposit);
        }

        // 3. Medimos el gas de la transferencia forzada
        uint256 gasBefore = gasleft();
        target.forceStakeTransfer(oldStaker, newStaker);
        uint256 gasUsed = gasBefore - gasleft();
        
        console.log("Gas consumido por forceStakeTransfer con %s elementos: %s", n, gasUsed);
    }
}
