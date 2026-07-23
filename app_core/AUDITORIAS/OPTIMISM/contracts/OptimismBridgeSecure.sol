// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title OptimismBridgeSecure
 * @dev Implementación corregida analizada por REMI-IA para mitigar vectores de reentrada.
 */
contract OptimismBridgeSecure {
    mapping(address => uint256) public balances;
    bool private _locked;

    event WithdrawalInitiated(address indexed recipient, uint256 amount);

    modifier nonReentrant() {
        require(!_locked, "REENTRANCY_GUARD_TRIGGERED");
        _locked = true;
        _;
        _locked = false;
    }

    constructor() {
        balances[msg.sender] = 5000;
    }

    /**
     * @notice Procesa retiros de fondos aplicando Checks-Effects-Interactions de forma segura.
     */
    function withdrawToL1(uint256 amount) external nonReentrant {
        // 1. CHECKS (Verificaciones)
        require(balances[msg.sender] >= amount, "INSUFFICIENT_FUNDS");

        // 2. EFFECTS (Efectos sobre el estado interno)
        balances[msg.sender] -= amount;

        // 3. INTERACTIONS (Llamadas externas e interacciones de bajo nivel)
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "TRANSFER_FAILED");

        emit WithdrawalInitiated(msg.sender, amount);
    }

    receive() external payable {}
}
