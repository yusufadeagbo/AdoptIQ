// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

contract BillingContract is AccessControl, ReentrancyGuard, Pausable {
    using SafeERC20 for IERC20;

    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant CHARGER_ROLE = keccak256("CHARGER_ROLE");

    struct Subscription {
        address subscriber;
        address token;
        uint256 amountPerCycle;
        uint256 cycleLength;
        uint256 nextChargeTime;
        bool active;
        uint256 totalPaid;
        uint256 cyclesPaid;
    }

    mapping(bytes32 => Subscription) public subscriptions;
    mapping(address => bytes32[]) public subscriberSubscriptions;
    mapping(address => bool) public supportedTokens;

    uint256 public totalSubscriptions;
    uint256 public totalRevenue;

    event SubscriptionCreated(
        bytes32 indexed subscriptionId,
        address indexed subscriber,
        address token,
        uint256 amountPerCycle,
        uint256 cycleLength
    );

    event SubscriptionCharged(
        bytes32 indexed subscriptionId,
        address indexed subscriber,
        uint256 amount,
        uint256 timestamp
    );

    event SubscriptionCanceled(
        bytes32 indexed subscriptionId,
        address indexed subscriber,
        uint256 timestamp
    );

    event SubscriptionUpdated(
        bytes32 indexed subscriptionId,
        uint256 newAmount,
        uint256 timestamp
    );

    event TokenSupportUpdated(
        address indexed token,
        bool supported
    );

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(CHARGER_ROLE, msg.sender);
    }

    function createSubscription(
        bytes32 subscriptionId,
        address token,
        uint256 amountPerCycle,
        uint256 cycleLength
    ) external whenNotPaused {
        require(supportedTokens[token], "Token not supported");
        require(subscriptions[subscriptionId].subscriber == address(0), "Subscription exists");
        require(amountPerCycle > 0, "Amount must be greater than 0");
        require(cycleLength > 0, "Cycle length must be greater than 0");

        IERC20 tokenContract = IERC20(token);
        uint256 allowance = tokenContract.allowance(msg.sender, address(this));
        require(allowance >= amountPerCycle, "Insufficient allowance");

        subscriptions[subscriptionId] = Subscription({
            subscriber: msg.sender,
            token: token,
            amountPerCycle: amountPerCycle,
            cycleLength: cycleLength,
            nextChargeTime: block.timestamp + cycleLength,
            active: true,
            totalPaid: 0,
            cyclesPaid: 0
        });

        subscriberSubscriptions[msg.sender].push(subscriptionId);
        totalSubscriptions++;

        emit SubscriptionCreated(
            subscriptionId,
            msg.sender,
            token,
            amountPerCycle,
            cycleLength
        );
    }

    function charge(bytes32 subscriptionId) external nonReentrant onlyRole(CHARGER_ROLE) {
        Subscription storage sub = subscriptions[subscriptionId];
        require(sub.active, "Subscription not active");
        require(block.timestamp >= sub.nextChargeTime, "Not yet time to charge");

        IERC20 tokenContract = IERC20(sub.token);
        uint256 allowance = tokenContract.allowance(sub.subscriber, address(this));
        require(allowance >= sub.amountPerCycle, "Insufficient allowance");

        tokenContract.safeTransferFrom(
            sub.subscriber,
            address(this),
            sub.amountPerCycle
        );

        sub.totalPaid += sub.amountPerCycle;
        sub.cyclesPaid++;
        sub.nextChargeTime = block.timestamp + sub.cycleLength;
        totalRevenue += sub.amountPerCycle;

        emit SubscriptionCharged(
            subscriptionId,
            sub.subscriber,
            sub.amountPerCycle,
            block.timestamp
        );
    }

    function cancelSubscription(bytes32 subscriptionId) external {
        Subscription storage sub = subscriptions[subscriptionId];
        require(sub.subscriber == msg.sender || hasRole(ADMIN_ROLE, msg.sender), "Not authorized");
        require(sub.active, "Already canceled");

        sub.active = false;

        emit SubscriptionCanceled(subscriptionId, sub.subscriber, block.timestamp);
    }

    function updateSubscription(
        bytes32 subscriptionId,
        uint256 newAmount
    ) external {
        Subscription storage sub = subscriptions[subscriptionId];
        require(sub.subscriber == msg.sender, "Not subscriber");
        require(sub.active, "Subscription not active");
        require(newAmount > 0, "Amount must be greater than 0");

        sub.amountPerCycle = newAmount;

        emit SubscriptionUpdated(subscriptionId, newAmount, block.timestamp);
    }

    function setSupportedToken(address token, bool supported) external onlyRole(ADMIN_ROLE) {
        supportedTokens[token] = supported;
        emit TokenSupportUpdated(token, supported);
    }

    function withdrawTokens(address token, uint256 amount) external onlyRole(ADMIN_ROLE) {
        IERC20(token).safeTransfer(msg.sender, amount);
    }

    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }

    function getSubscription(bytes32 subscriptionId) external view returns (
        address subscriber,
        address token,
        uint256 amountPerCycle,
        uint256 cycleLength,
        uint256 nextChargeTime,
        bool active,
        uint256 totalPaid,
        uint256 cyclesPaid
    ) {
        Subscription memory sub = subscriptions[subscriptionId];
        return (
            sub.subscriber,
            sub.token,
            sub.amountPerCycle,
            sub.cycleLength,
            sub.nextChargeTime,
            sub.active,
            sub.totalPaid,
            sub.cyclesPaid
        );
    }

    function getSubscriberSubscriptions(address subscriber) external view returns (bytes32[] memory) {
        return subscriberSubscriptions[subscriber];
    }
}
