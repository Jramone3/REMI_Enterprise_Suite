// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.19;

import "forge-std/Test.sol";

// DEFINIMOS SOLO LA INTERFAZ, NO IMPORTAMOS EL ARCHIVO .SOL ANTIGUO
interface IL1GraphTokenGateway {
    function initialize(address _controller) external;
    function setL2MintAllowance(uint256 _allowance) external;
    function mint(address _to, uint256 _amount) external;
    function l1Token() external view returns (address);
}

contract InflationPoC is Test {
    IL1GraphTokenGateway public gateway;
    address public controller = address(0x1337);

    function setUp() public {
        // En lugar de 'new L1GraphTokenGateway()', 
        // desplegamos el bytecode directamente o usamos un mock
        // Por ahora, asumiremos la dirección donde está el contrato
        gateway = IL1GraphTokenGateway(0x...); // Si tienes la address, úsala
    }
}
