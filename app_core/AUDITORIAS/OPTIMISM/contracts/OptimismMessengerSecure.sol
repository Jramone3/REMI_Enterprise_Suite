// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title OptimismMessengerSecure
 * @dev Mitigación de Replay Attacks en mensajería Cross-Domain mediante registro de hashes únicos.
 */
contract OptimismMessengerSecure {
    // Mapeo para registrar de forma permanente los mensajes ya ejecutados
    mapping(bytes32 => bool) public successfulMessages;
    mapping(address => uint256) public balances;
    uint256 public vaultBalance;

    event RelayedMessage(bytes32 indexed msgHash);
    event FailedMessage(bytes32 indexed msgHash);

    constructor() {
        vaultBalance = 10000;
    }

    /**
     * @notice Ejecuta un mensaje proveniente de L1 verificando que no haya sido replicado.
     */
    function executeCrossDomainMessage(
        bytes32 msgHash,
        address targetUser,
        uint256 amount
    ) external {
        // 1. CHECKS: Validar que el mensaje NO haya sido ejecutado antes
        require(!successfulMessages[msgHash], "REPLAY_ATTACK_DETECTED");
        require(vaultBalance >= amount, "INSUFFICIENT_VAULT_LIQUIDITY");

        // 2. EFFECTS: Marcar el hash del mensaje como ejecutado INMEDIATAMENTE
        successfulMessages[msgHash] = true;
        
        // 3. INTERACTIONS: Transferencia o acuñación de los fondos
        vaultBalance -= amount;
        balances[targetUser] += amount;

        emit RelayedMessage(msgHash);
    }
}
