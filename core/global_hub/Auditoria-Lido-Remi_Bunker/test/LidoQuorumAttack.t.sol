// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "forge-std/Test.sol";
import "../src/Lido_Core/LidoQuorum.sol";

contract LidoQuorumTest is Test {
    LidoQuorum quorum;
    address[] oracles = [address(1), address(2), address(3)];

    function setUp() public {
        quorum = new LidoQuorum(oracles);
    }

    function testSybilAttack() public {
        // REMI simula un ataque Sybil: Un solo atacante controla address(1) y address(2)
        vm.prank(address(1));
        quorum.submitVote(1, 500 ether);

        vm.prank(address(2));
        quorum.submitVote(1, 500 ether);

        emit log_named_uint("Votos acumulados por el mismo atacante", quorum.votes(1) / 1e18);
        emit log("RESULTADO: El atacante ya tiene la mayoria (1000 ETH) con solo dos llaves.");
    }
}
