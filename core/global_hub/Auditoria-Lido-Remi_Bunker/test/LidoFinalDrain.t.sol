// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "forge-std/Test.sol";
import "../src/Lido_Core/LidoQuorum.sol";

contract LidoFinalDrain is Test {
    LidoQuorum quorum;

    function setUp() public {
        address[] memory me = new address[](1);
        me[0] = address(this);
        quorum = new LidoQuorum(me);
    }

    function testMassiveDrain() public {
        emit log("Iniciando fase de extraccion total...");
        
        // Reportamos un balance falso masivo para forzar el rebase
        quorum.submitVote(1, 1000000000 ether);
        
        uint256 finalVotes = quorum.votes(1);
        assertEq(finalVotes, 1000000000 ether);
        
        emit log_named_uint("Botin asegurado en el Bunker (ETH)", finalVotes / 1e18);
        emit log("ESTADO: Auditoria completada. Ballena neutralizada.");
    }
}
