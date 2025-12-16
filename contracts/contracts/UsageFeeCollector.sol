// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./Treasury.sol";

/**
 * @title UsageFeeCollector
 * @dev Recurring revenue from API calls and premium features
 */
contract UsageFeeCollector is Ownable {
    address public treasury;
    
    mapping(address => uint256) public usageCredits; // user => credits
    uint256 public constant CREDIT_PRICE = 0.0001 ether; // Price per credit
    uint256 public constant CREDITS_PER_1000_CALLS = 1;
    
    // Events
    event CreditsPurchased(address indexed user, uint256 amount, uint256 cost);
    event CreditsConsumed(address indexed user, uint256 credits);
    
    constructor(address _treasury) Ownable(msg.sender) {
        require(_treasury != address(0), "Invalid treasury address");
        treasury = _treasury;
    }
    
    /**
     * @dev Purchase usage credits
     * @param amount Number of credits to purchase
     */
    function purchaseCredits(uint256 amount) external payable {
        uint256 cost = amount * CREDIT_PRICE;
        require(msg.value >= cost, "Insufficient payment");
        
        usageCredits[msg.sender] += amount;
        
        // Send to treasury
        (bool success, ) = treasury.call{value: msg.value}("");
        require(success, "Treasury transfer failed");
        
        emit CreditsPurchased(msg.sender, amount, msg.value);
    }
    
    /**
     * @dev Consume credits (called by platform services)
     * @param user The user address
     * @param calls Number of API calls made
     */
    function consumeCredits(address user, uint256 calls) external {
        // Only authorized services can call this
        // In production, add access control
        uint256 creditsNeeded = (calls / 1000) * CREDITS_PER_1000_CALLS;
        if (calls % 1000 != 0) {
            creditsNeeded += 1; // Round up
        }
        
        require(usageCredits[user] >= creditsNeeded, "Insufficient credits");
        usageCredits[user] -= creditsNeeded;
        
        emit CreditsConsumed(user, creditsNeeded);
    }
    
    /**
     * @dev Get user's credit balance
     */
    function getCredits(address user) external view returns (uint256) {
        return usageCredits[user];
    }
    
    /**
     * @dev Set treasury address (only owner)
     */
    function setTreasury(address _treasury) external onlyOwner {
        require(_treasury != address(0), "Invalid treasury address");
        treasury = _treasury;
    }
}

