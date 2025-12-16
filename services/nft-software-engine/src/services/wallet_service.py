"""
Wallet Service for NFT Software Engine
Handles wallet generation, management, and secure storage
"""

import uuid
import json
from typing import Optional, Dict, Any
from eth_account import Account
from eth_account.messages import encode_defunct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from cryptography.fernet import Fernet
import structlog

from ..models.customer import Customer
from ..models.wallet import Wallet
from ..core.database import get_db

logger = structlog.get_logger(__name__)


class WalletService:
    """
    Service for managing Ethereum wallets for customers
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize wallet service
        
        Args:
            encryption_key: Base64 encoded encryption key for private keys
                            If not provided, will use ENCRYPTION_KEY from environment
        """
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # This should be loaded from environment variables in production
            self.cipher = Fernet(Fernet.generate_key())
    
    async def create_wallet_for_customer(
        self,
        db: AsyncSession,
        customer_id: str,
        customer_email: str,
        customer_name: Optional[str] = None,
        customer_company: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new wallet for a customer
        
        Args:
            db: Database session
            customer_id: Unique customer identifier
            customer_email: Customer email
            customer_name: Optional customer name
            customer_company: Optional customer company
            
        Returns:
            Dictionary containing wallet information (address, customer_id)
            Note: Private key is encrypted and stored, not returned
        """
        try:
            # Check if customer exists
            customer_query = select(Customer).where(Customer.customer_id == customer_id)
            customer_result = await db.execute(customer_query)
            customer = customer_result.scalar_one_or_none()
            
            if not customer:
                # Create new customer
                customer = Customer(
                    customer_id=customer_id,
                    email=customer_email,
                    name=customer_name,
                    company=customer_company
                )
                db.add(customer)
                await db.flush()
                logger.info("Created new customer", customer_id=customer_id, email=customer_email)
            
            # Check if customer already has an active wallet
            existing_wallet_query = select(Wallet).where(
                and_(
                    Wallet.customer_id == customer.id,
                    Wallet.is_active == True
                )
            )
            existing_result = await db.execute(existing_wallet_query)
            existing_wallet = existing_result.scalar_one_or_none()
            
            if existing_wallet:
                raise ValueError(f"Customer {customer_id} already has an active wallet")
            
            # Generate new Ethereum wallet
            account = Account.create()
            wallet_address = account.address
            private_key = account.key.hex()
            
            # Encrypt private key
            encrypted_private_key = self.cipher.encrypt(private_key.encode()).decode()
            
            # Create wallet record
            wallet = Wallet(
                customer_id=customer.id,
                wallet_address=wallet_address,
                private_key_encrypted=encrypted_private_key,
                is_active=True,
                blockchain_network="ethereum"
            )
            db.add(wallet)
            await db.flush()
            
            logger.info("Created wallet for customer", 
                       customer_id=customer_id, 
                       wallet_address=wallet_address)
            
            return {
                "address": wallet_address,
                "customer_id": customer_id,
                "customer_email": customer_email,
                "wallet_id": wallet.id
            }
            
        except Exception as e:
            logger.error("Error creating wallet", customer_id=customer_id, error=str(e))
            raise
    
    async def get_wallet_by_address(self, db: AsyncSession, wallet_address: str) -> Optional[Wallet]:
        """
        Retrieve wallet by address
        
        Args:
            db: Database session
            wallet_address: Ethereum wallet address
            
        Returns:
            Wallet object or None if not found
        """
        try:
            query = select(Wallet).where(Wallet.wallet_address == wallet_address)
            result = await db.execute(query)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error("Error retrieving wallet", wallet_address=wallet_address, error=str(e))
            return None
    
    async def get_customer_wallets(self, db: AsyncSession, customer_id: str) -> list[Dict[str, Any]]:
        """
        Get all wallets for a customer
        
        Args:
            db: Database session
            customer_id: Customer identifier
            
        Returns:
            List of wallet information dictionaries
        """
        try:
            # Get customer
            customer_query = select(Customer).where(Customer.customer_id == customer_id)
            customer_result = await db.execute(customer_query)
            customer = customer_result.scalar_one_or_none()
            
            if not customer:
                return []
            
            # Get customer wallets
            wallets_query = select(Wallet).where(Wallet.customer_id == customer.id)
            wallets_result = await db.execute(wallets_query)
            wallets = wallets_result.scalars().all()
            
            return [
                {
                    "address": wallet.wallet_address,
                    "is_active": wallet.is_active,
                    "blockchain_network": wallet.blockchain_network,
                    "created_at": wallet.created_at.isoformat(),
                    "wallet_id": wallet.id
                }
                for wallet in wallets
            ]
            
        except Exception as e:
            logger.error("Error retrieving customer wallets", customer_id=customer_id, error=str(e))
            return []
    
    def sign_message(self, private_key_hex: str, message: str) -> str:
        """
        Sign a message with a private key
        
        Args:
            private_key_hex: Hex-encoded private key
            message: Message to sign
            
        Returns:
            Signature as hex string
        """
        try:
            account = Account.from_key(private_key_hex)
            message_bytes = message.encode('utf-8')
            signed_message = account.sign_message(encode_defunct(message_bytes))
            return signed_message.signature.hex()
        except Exception as e:
            logger.error("Error signing message", error=str(e))
            raise ValueError(f"Failed to sign message: {str(e)}")
    
    def verify_signature(self, address: str, message: str, signature: str) -> bool:
        """
        Verify a signature against an address
        
        Args:
            address: Ethereum address
            message: Original message
            signature: Hex signature
            
        Returns:
            True if signature is valid
        """
        try:
            message_bytes = message.encode('utf-8')
            recovered_address = Account.recover_message(
                encode_defunct(message_bytes), 
                signature=bytes.fromhex(signature)
            )
            return recovered_address.lower() == address.lower()
        except Exception as e:
            logger.error("Error verifying signature", error=str(e))
            return False


# Global wallet service instance
wallet_service = WalletService()
