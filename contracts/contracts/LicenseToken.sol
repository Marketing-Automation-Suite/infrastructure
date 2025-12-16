// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/common/ERC2981.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "./Treasury.sol";

/**
 * @title LicenseToken
 * @dev ERC-721 NFT contract for marketing platform licenses with revenue guarantees
 * Features:
 * - 10% platform fee on primary sales (guaranteed revenue)
 * - 10% royalty on secondary sales (EIP-2981 standard)
 * - Referral reward system (viral growth)
 * - Tier-based pricing (Bronze, Silver, Gold)
 */
contract LicenseToken is ERC721, ERC721URIStorage, ERC2981, Ownable {
    using Counters for Counters.Counter;
    
    // Revenue mechanisms
    uint256 public constant PLATFORM_FEE_BPS = 1000; // 10%
    uint256 public constant ROYALTY_FEE_BPS = 1000; // 10%
    address public treasury; // Treasury contract address
    
    // Token counter
    Counters.Counter private _tokenIdCounter;
    
    // Tier pricing (guaranteed minimum revenue)
    mapping(string => uint256) public tierPrices;
    
    // Token metadata
    mapping(uint256 => string) private _tiers; // tokenId => tier
    mapping(uint256 => address) private _referrers; // tokenId => referrer address
    
    // Referral tracking
    mapping(address => address) public userReferrers; // user => referrer
    mapping(address => uint256) public referralRewards; // referrer => total rewards
    mapping(address => uint256) public referralCount; // referrer => count
    
    // Revenue tracking
    uint256 public totalRevenue;
    uint256 public totalRoyalties;
    uint256 public totalReferralRewards;
    uint256 public totalPlatformFees;
    
    // Events
    event LicenseMinted(address indexed to, uint256 indexed tokenId, string tier, uint256 price);
    event ReferralRewardPaid(address indexed referrer, uint256 amount);
    event PlatformFeeCollected(uint256 amount);
    
    constructor(address _treasury) ERC721("Marketing Platform License", "MPL") Ownable(msg.sender) {
        treasury = _treasury;
        
        // Set tier prices (in wei)
        tierPrices["bronze"] = 0.01 ether;
        tierPrices["silver"] = 0.05 ether;
        tierPrices["gold"] = 0.1 ether;
        
        // Set default royalty to 10%
        _setDefaultRoyalty(treasury, ROYALTY_FEE_BPS);
    }
    
    /**
     * @dev Mint a license token for a specific tier
     * @param tier The tier to mint (bronze, silver, gold)
     * @param referrer The address of the referrer (optional, can be address(0))
     */
    function mintLicense(string memory tier, address referrer) external payable {
        uint256 price = tierPrices[tier];
        require(price > 0, "Invalid tier");
        require(msg.value >= price, "Insufficient payment");
        
        // Calculate platform fee (10% - guaranteed revenue)
        uint256 platformFee = (msg.value * PLATFORM_FEE_BPS) / 10000;
        uint256 netAmount = msg.value - platformFee;
        
        // Send platform fee to treasury (guaranteed revenue)
        (bool success, ) = treasury.call{value: platformFee}("");
        require(success, "Treasury transfer failed");
        emit PlatformFeeCollected(platformFee);
        totalPlatformFees += platformFee;
        
        // Handle referral rewards (viral growth)
        if (referrer != address(0) && userReferrers[msg.sender] == address(0) && referrer != msg.sender) {
            userReferrers[msg.sender] = referrer;
            referralCount[referrer] += 1;
            
            // Calculate referral reward (10% of purchase)
            uint256 referralReward = price / 10;
            referralRewards[referrer] += referralReward;
            totalReferralRewards += referralReward;
            
            // Apply network effect multipliers
            uint256 multiplier = getReferralMultiplier(referrer);
            uint256 finalReward = (referralReward * multiplier) / 100;
            
            // Send referral reward
            (success, ) = referrer.call{value: finalReward}("");
            require(success, "Referral transfer failed");
            emit ReferralRewardPaid(referrer, finalReward);
        }
        
        // Mint token
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        _mint(msg.sender, tokenId);
        _tiers[tokenId] = tier;
        if (referrer != address(0)) {
            _referrers[tokenId] = referrer;
        }
        
        // Track revenue
        totalRevenue += msg.value;
        
        emit LicenseMinted(msg.sender, tokenId, tier, msg.value);
    }
    
    /**
     * @dev Get referral multiplier based on referral count
     * @param referrer The referrer address
     * @return multiplier The multiplier percentage (100 = base, 110 = 10% bonus, etc.)
     */
    function getReferralMultiplier(address referrer) public view returns (uint256) {
        uint256 count = referralCount[referrer];
        if (count >= 100) {
            return 150; // 50% bonus for 100+ referrals
        } else if (count >= 50) {
            return 125; // 25% bonus for 50+ referrals
        } else if (count >= 10) {
            return 110; // 10% bonus for 10+ referrals
        }
        return 100; // Base multiplier
    }
    
    /**
     * @dev Get tier for a token
     * @param tokenId The token ID
     * @return The tier string
     */
    function getTier(uint256 tokenId) external view returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "Token does not exist");
        return _tiers[tokenId];
    }
    
    /**
     * @dev Verify license ownership
     * @param owner The address to check
     * @param tokenId The token ID
     * @return Whether the address owns the token
     */
    function verifyLicense(address owner, uint256 tokenId) external view returns (bool) {
        return ownerOf(tokenId) == owner;
    }
    
    /**
     * @dev Get referrer for a token
     * @param tokenId The token ID
     * @return The referrer address
     */
    function getReferrer(uint256 tokenId) external view returns (address) {
        return _referrers[tokenId];
    }
    
    /**
     * @dev Update tier price (only owner)
     */
    function setTierPrice(string memory tier, uint256 price) external onlyOwner {
        tierPrices[tier] = price;
    }
    
    /**
     * @dev Update treasury address (only owner)
     */
    function setTreasury(address _treasury) external onlyOwner {
        require(_treasury != address(0), "Invalid treasury address");
        treasury = _treasury;
        _setDefaultRoyalty(treasury, ROYALTY_FEE_BPS);
    }
    
    /**
     * @dev Set token URI (only owner, for metadata)
     */
    function setTokenURI(uint256 tokenId, string memory uri) external onlyOwner {
        _setTokenURI(tokenId, uri);
    }
    
    /**
     * @dev Get revenue statistics
     */
    function getRevenueStats() external view returns (
        uint256 _totalRevenue,
        uint256 _totalPlatformFees,
        uint256 _totalReferralRewards,
        uint256 _totalRoyalties
    ) {
        return (totalRevenue, totalPlatformFees, totalReferralRewards, totalRoyalties);
    }
    
    // Override required by Solidity
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage, ERC2981)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
    
    // EIP-2981 Royalty Standard (guaranteed secondary market revenue)
    function royaltyInfo(uint256 /* tokenId */, uint256 salePrice) 
        public view override returns (address receiver, uint256 royaltyAmount) {
        return (treasury, (salePrice * ROYALTY_FEE_BPS) / 10000);
    }
}

