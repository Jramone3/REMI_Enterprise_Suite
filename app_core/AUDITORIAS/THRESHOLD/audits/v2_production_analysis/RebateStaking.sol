// SPDX-License-Identifier: GPL-3.0-only
pragma solidity 0.8.17;

import "@openzeppelin/contracts-upgradeable/token/ERC20/IERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/utils/SafeERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/math/SafeCastUpgradeable.sol";

contract RebateStaking is Initializable, OwnableUpgradeable {
    using SafeERC20Upgradeable for IERC20Upgradeable;

    error CallerNotBridge();
    error ParametersCannotBeZero();
    error RollingWindowCannotBeZero();
    error AmountCannotBeZero();
    error UnstakingAlreadyStarted();
    error AmountTooBig();
    error NoUnstakingProcess();
    error UnstakingNotFinished();
    error ZeroAddress();
    error NotAStaker();
    error WrongDelegatee();
    error AddressAlreadyTaken();

    enum RebateTreasuryFeeMode { Both, DepositOnly, RedemptionOnly }
    enum TreasuryFeeType { Deposit, Redemption }

    struct Rebate {
        uint32 timestamp;
        uint64 feeRebate;
        uint256[50] __gap;
    }

    struct Stake {
        uint96 stakedAmount;
        uint96 unstakingAmount;
        uint32 unstakingTimestamp;
        uint256 rollingWindowStartIndex;
        Rebate[] rebates;
        RebateTreasuryFeeMode rebateTreasuryFeeMode;
        address delegatee;
    }

    IERC20Upgradeable public token;
    address public bridge;
    uint256 public rollingWindow;
    uint256 public unstakingPeriod;
    uint256 public rebatePerToken;
    mapping(address => Stake) public stakes;
    mapping(address => address) public delegates;
    uint256[49] private __gap;

    event RollingWindowUpdated(uint256 rollingWindow);
    event UnstakingPeriodUpdated(uint256 unstakingPeriod);
    event RebatePerTokenUpdated(uint256 rebatePerToken);
    event RebateReceived(address staker, uint64 rebate);
    event RebateCanceled(address staker, uint256 requestedAt);
    event RebateTreasuryFeeModeUpdated(address indexed staker, RebateTreasuryFeeMode rebateTreasuryFeeMode);
    event Staked(address staker, uint256 amount);
    event UnstakeStarted(address staker, uint256 amount);
    event UnstakeFinished(address staker, uint256 amount);
    event DelegateeSet(address staker, address delegatee);
    event TransferFinished(address oldStaker, address newStaker);

    constructor() { _disableInitializers(); }

    modifier onlyBridge() { if (msg.sender != address(bridge)) revert CallerNotBridge(); _; }

    function initialize(address _bridge, address _token, uint256 _rollingWindow, uint256 _unstakingPeriod, uint256 _rebatePerToken) external initializer {
        if (_bridge == address(0) || _token == address(0) || _rollingWindow == 0) revert ParametersCannotBeZero();
        bridge = _bridge;
        token = IERC20Upgradeable(_token);
        rollingWindow = _rollingWindow;
        unstakingPeriod = _unstakingPeriod;
        rebatePerToken = _rebatePerToken;
        __Ownable_init();
    }

    function updateRollingWindow(uint256 _newRollingWindow) external onlyOwner {
        if (_newRollingWindow == 0) revert RollingWindowCannotBeZero();
        rollingWindow = _newRollingWindow;
        emit RollingWindowUpdated(rollingWindow);
    }

    function updateUnstakingPeriod(uint256 _newUnstakingPeriod) external onlyOwner {
        unstakingPeriod = _newUnstakingPeriod;
        emit UnstakingPeriodUpdated(unstakingPeriod);
    }

    function updateRebatePerToken(uint256 _newRebatePerToken) external onlyOwner {
        rebatePerToken = _newRebatePerToken;
        emit RebatePerTokenUpdated(rebatePerToken);
    }

    function setRebateTreasuryFeeMode(RebateTreasuryFeeMode _rebateTreasuryFeeMode) external {
        stakes[msg.sender].rebateTreasuryFeeMode = _rebateTreasuryFeeMode;
        emit RebateTreasuryFeeModeUpdated(msg.sender, _rebateTreasuryFeeMode);
    }

    function setDelegatee(address _delegatee) external {
        Stake storage stakeInfo = stakes[msg.sender];
        if (stakeInfo.stakedAmount == 0) revert NotAStaker();
        if (stakeInfo.delegatee != address(0)) delegates[stakeInfo.delegatee] = address(0);
        if (_delegatee == address(0) || _delegatee == msg.sender) {
            stakeInfo.delegatee = address(0);
            emit DelegateeSet(msg.sender, msg.sender);
            return;
        }
        if (delegates[_delegatee] != address(0) || stakes[_delegatee].stakedAmount != 0) revert WrongDelegatee();
        stakeInfo.delegatee = _delegatee;
        delegates[_delegatee] = msg.sender;
        emit DelegateeSet(msg.sender, _delegatee);
    }

    function getRebateCap(address user) external view returns (uint64) {
        return getRebateCap(stakes[user]);
    }

    function getRebateCap(Stake storage stakeInfo) internal view returns (uint64) {
        if (rebatePerToken == 0) return 0;
        return SafeCastUpgradeable.toUint64((stakeInfo.stakedAmount - stakeInfo.unstakingAmount) / rebatePerToken);
    }

    function getAvailableRebate(address user) external view returns (uint64 rebateInWindow) {
        Stake storage stakeInfo = stakes[user];
        uint64 rebateCap = getRebateCap(stakeInfo);
        if (rebateCap == 0) return 0;
        if (stakeInfo.rebates.length == 0) return rebateCap;
        uint256 windowStart = block.timestamp - rollingWindow;
        for (uint256 i = stakeInfo.rollingWindowStartIndex; i < stakeInfo.rebates.length; i++) {
            if (stakeInfo.rebates[i].timestamp >= windowStart) rebateInWindow += stakeInfo.rebates[i].feeRebate;
        }
        return rebateCap - rebateInWindow;
    }

    function getRebateInRollingWindow(Stake storage stakeInfo) internal returns (uint64 rebateInWindow) {
        if (stakeInfo.rebates.length == 0) return 0;
        uint256 windowStart = block.timestamp - rollingWindow;
        for (uint256 i = stakeInfo.rollingWindowStartIndex; i < stakeInfo.rebates.length; i++) {
            if (stakeInfo.rebates[i].timestamp < windowStart) stakeInfo.rollingWindowStartIndex++;
            else rebateInWindow += stakeInfo.rebates[i].feeRebate;
        }
        return rebateInWindow;
    }

    function applyForRebate(address user, uint64 treasuryFee, TreasuryFeeType treasuryFeeType) external onlyBridge returns (uint64) {
        user = getStaker(user);
        Stake storage stakeInfo = stakes[user];
        if (!isRebateEnabled(user, treasuryFeeType)) return treasuryFee;
        uint64 rebateCap = getRebateCap(stakeInfo);
        if (rebateCap == 0) return treasuryFee;
        uint64 currentRebate = getRebateInRollingWindow(stakeInfo);
        if (rebateCap <= currentRebate) return treasuryFee;
        uint64 rebate = rebateCap - currentRebate;
        if (rebate > treasuryFee) rebate = treasuryFee;
        Rebate storage value = stakeInfo.rebates.push();
        value.timestamp = uint32(block.timestamp);
        value.feeRebate = rebate;
        emit RebateReceived(user, rebate);
        return treasuryFee - rebate;
    }

    function isRebateEnabled(address user, TreasuryFeeType treasuryFeeType) internal view returns (bool) {
        RebateTreasuryFeeMode mode = stakes[user].rebateTreasuryFeeMode;
        return mode == RebateTreasuryFeeMode.Both || (mode == RebateTreasuryFeeMode.DepositOnly && treasuryFeeType == TreasuryFeeType.Deposit) || (mode == RebateTreasuryFeeMode.RedemptionOnly && treasuryFeeType == TreasuryFeeType.Redemption);
    }

    function getStaker(address user) internal view returns (address) {
        address staker = delegates[user];
        if (stakes[user].stakedAmount == 0 && staker != address(0)) return staker;
        return user;
    }

    function cancelRebate(address user, uint256 requestedAt) external onlyBridge {
        user = getStaker(user);
        Stake storage stakeInfo = stakes[user];
        if (stakeInfo.stakedAmount == 0) return;
        uint256 windowStart = block.timestamp - rollingWindow;
        for (uint256 i = stakeInfo.rollingWindowStartIndex; i < stakeInfo.rebates.length; i++) {
            if (stakeInfo.rebates[i].timestamp > requestedAt) break;
            else if (stakeInfo.rebates[i].timestamp < windowStart) stakeInfo.rollingWindowStartIndex++;
            else if (requestedAt == stakeInfo.rebates[i].timestamp) { stakeInfo.rebates[i].feeRebate = 0; emit RebateCanceled(user, requestedAt); break; }
        }
    }

    function stake(uint96 amount) external {
        if (amount == 0) revert AmountCannotBeZero();
        address otherStaker = delegates[msg.sender];
        if (otherStaker != address(0)) {
            stakes[otherStaker].delegatee = address(0);
            delegates[msg.sender] = address(0);
            emit DelegateeSet(otherStaker, otherStaker);
        }
        stakes[msg.sender].stakedAmount += amount;
        emit Staked(msg.sender, amount);
        token.safeTransferFrom(msg.sender, address(this), amount);
    }

    function startUnstaking(uint96 amount) external {
        if (amount == 0) revert AmountCannotBeZero();
        Stake storage stakeInfo = stakes[msg.sender];
        if (stakeInfo.unstakingTimestamp != 0) revert UnstakingAlreadyStarted();
        if (amount > stakeInfo.stakedAmount) revert AmountTooBig();
        stakeInfo.unstakingTimestamp = uint32(block.timestamp);
        stakeInfo.unstakingAmount = amount;
        emit UnstakeStarted(msg.sender, amount);
    }

    function finalizeUnstaking(address receiver) external {
        if (receiver == address(0)) revert ZeroAddress();
        Stake storage stakeInfo = stakes[msg.sender];
        if (stakeInfo.unstakingTimestamp == 0) revert NoUnstakingProcess();
        if (stakeInfo.unstakingTimestamp + unstakingPeriod > block.timestamp) revert UnstakingNotFinished();
        stakeInfo.stakedAmount -= stakeInfo.unstakingAmount;
        uint96 amount = stakeInfo.unstakingAmount;
        stakeInfo.unstakingTimestamp = 0;
        stakeInfo.unstakingAmount = 0;
        if (stakeInfo.stakedAmount == 0 && stakeInfo.delegatee != address(0)) {
            delegates[stakeInfo.delegatee] = address(0);
            stakeInfo.delegatee = address(0);
        }
        emit UnstakeFinished(msg.sender, amount);
        token.safeTransfer(receiver, amount);
    }

    function getRebateLength(address user) external view returns (uint256) { return stakes[user].rebates.length; }
    function getRebate(address user, uint256 index) external view returns (uint32 timestamp, uint64 feeRebate) {
        Rebate storage r = stakes[user].rebates[index];
        return (r.timestamp, r.feeRebate);
    }
    function getStake(address user) external view returns (uint96 stakedAmount) { return stakes[user].stakedAmount; }
    function getUnstakingAmount(address user) external view returns (uint96 unstakingAmount, uint32 unstakingTimestamp) {
        return (stakes[user].unstakingAmount, stakes[user].unstakingTimestamp);
    }
    function getRebateTreasuryFeeMode(address user) external view returns (RebateTreasuryFeeMode mode) { return stakes[user].rebateTreasuryFeeMode; }
    function getDelegatee(address user) external view returns (address) { return stakes[user].delegatee; }

    function forceStakeTransfer(address oldStaker, address newStaker) external onlyOwner {
        if (oldStaker == address(0) || newStaker == address(0)) revert ZeroAddress();
        Stake storage oldStake = stakes[oldStaker];
        if (oldStake.stakedAmount == 0) revert NotAStaker();
        Stake storage newStake = stakes[newStaker];
        if (newStake.stakedAmount != 0 || delegates[newStaker] != address(0)) revert AddressAlreadyTaken();
        newStake.stakedAmount = oldStake.stakedAmount;
        newStake.unstakingAmount = oldStake.unstakingAmount;
        newStake.unstakingTimestamp = oldStake.unstakingTimestamp;
        newStake.rebateTreasuryFeeMode = oldStake.rebateTreasuryFeeMode;
        newStake.rollingWindowStartIndex = oldStake.rollingWindowStartIndex;
        for (uint256 i = 0; i < oldStake.rebates.length; i++) newStake.rebates.push(oldStake.rebates[i]);
        if (oldStake.delegatee != address(0)) {
            address d = oldStake.delegatee;
            newStake.delegatee = d;
            delegates[d] = newStaker;
            oldStake.delegatee = address(0);
            emit DelegateeSet(newStaker, d);
        }
        oldStake.stakedAmount = 0;
        oldStake.unstakingAmount = 0;
        oldStake.unstakingTimestamp = 0;
        oldStake.rebateTreasuryFeeMode = RebateTreasuryFeeMode.Both;
        oldStake.rollingWindowStartIndex = 0;
        emit TransferFinished(oldStaker, newStaker);
    }
}
