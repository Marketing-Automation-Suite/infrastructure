// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title Treasury
 * @dev Revenue collection and distribution contract
 * Features:
 * - Automatic withdrawal at threshold
 * - Revenue tracking
 * - Multi-signature support (future)
 */
contract Treasury is Ownable {
    // Revenue streams
    uint256 public totalCollected;
    uint256 public totalDistributed;
    address public revenueRecipient; // Owner wallet
    
    // Automatic withdrawal threshold
    uint256 public withdrawalThreshold = 1 ether; // Auto-withdraw at 1 ETH
    
    // Events
    event RevenueCollected(uint256 amount, address from);
    event RevenueWithdrawn(uint256 amount, address to);
    event ThresholdUpdated(uint256 newThreshold);
    event RecipientUpdated(address newRecipient);
    
    constructor(address _revenueRecipient) Ownable(msg.sender) {
        require(_revenueRecipient != address(0), "Invalid recipient address");
        revenueRecipient = _revenueRecipient;
    }
    
    /**
     * @dev Collect revenue from all sources
     */
    receive() external payable {
        totalCollected += msg.value;
        emit RevenueCollected(msg.value, msg.sender);
        
        // Auto-withdraw if threshold reached
        if (address(this).balance >= withdrawalThreshold) {
            withdraw();
        }
    }
    
    /**
     * @dev Fallback function
     */
    fallback() external payable {
        receive();
    }
    
    /**
     * @dev Withdraw funds to revenue recipient
     */
    function withdraw() public {
        require(
            msg.sender == owner() || address(this).balance >= withdrawalThreshold,
            "Unauthorized or below threshold"
        );
        
        uint256 amount = address(this).balance;
        require(amount > 0, "No funds to withdraw");
        
        totalDistributed += amount;
        
        (bool success, ) = revenueRecipient.call{value: amount}("");
        require(success, "Withdrawal failed");
        
        emit RevenueWithdrawn(amount, revenueRecipient);
    }
    
    /**
     * @dev Set withdrawal threshold (only owner)
     */
    function setWithdrawalThreshold(uint256 _threshold) external onlyOwner {
        withdrawalThreshold = _threshold;
        emit ThresholdUpdated(_threshold);
    }
    
    /**
     * @dev Set revenue recipient (only owner)
     */
    function setRevenueRecipient(address _recipient) external onlyOwner {
        require(_recipient != address(0), "Invalid recipient address");
        revenueRecipient = _recipient;
        emit RecipientUpdated(_recipient);
    }
    
    /**
     * @dev Get revenue statistics
     */
    function getRevenueStats() external view returns (
        uint256 collected,
        uint256 distributed,
        uint256 balance
    ) {
        return (totalCollected, totalDistributed, address(this).balance);
    }
}

