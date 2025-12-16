"""
Token verification and management service
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..models.database import TokenTransaction, TransactionStatus, PaymentMethod
from ..models.schemas import (
    TokenVerificationResponse, WalletTokensResponse, PurchaseNFTRequest, 
    VerifyTokenRequest, TransferTokenRequest
)
from ..core.nft_manager import NFTManager
from ..config.settings import settings

logger = logging.getLogger(__name__)


class TokenService:
    """Service for token verification and management"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.nft_manager = NFTManager(db_session)
    
    def verify_token_ownership(
        self,
        wallet_address: str,
        product_id: int,
        tier: str = None
    ) -> TokenVerificationResponse:
        """Verify token ownership for wallet"""
        return self.nft_manager.verify_token_ownership(
            wallet_address, product_id, tier
        )
    
    def purchase_token(
        self,
        product_id: int,
        tier: str,
        wallet_address: str,
        user_id: int = None,
        payment_method: str = "crypto"
    ) -> Dict[str, Any]:
        """Purchase NFT token"""
        return self.nft_manager.purchase_token(
            product_id, tier, wallet_address, user_id, payment_method
        )
    
    def transfer_token(
        self,
        token_id: str,
        from_wallet: str,
        to_wallet: str
    ) -> Dict[str, Any]:
        """Transfer NFT token between wallets"""
        return self.nft_manager.transfer_token(token_id, from_wallet, to_wallet)
    
    def get_user_tokens(self, wallet_address: str) -> WalletTokensResponse:
        """Get all tokens owned by wallet"""
        try:
            tokens = self.nft_manager.get_user_tokens(wallet_address)
            
            # Calculate total value (simplified)
            total_value = sum(
                token.get("price", 0) for token in tokens 
                if token.get("price")
            )
            
            return WalletTokensResponse(
                wallet_address=wallet_address,
                tokens=tokens,
                total_value=total_value,
                network=settings.DEFAULT_NETWORK if hasattr(settings, 'DEFAULT_NETWORK') else "polygon"
            )
            
        except Exception as e:
            logger.error(f"Failed to get user tokens for {wallet_address}: {e}")
            return WalletTokensResponse(
                wallet_address=wallet_address,
                tokens=[],
                total_value=0.0
            )
    
    def get_transaction_status(self, transaction_hash: str) -> Optional[Dict[str, Any]]:
        """Get transaction status by hash"""
        try:
            transaction = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.transaction_hash == transaction_hash
            ).first()
            
            if transaction:
                return {
                    "id": transaction.id,
                    "status": transaction.status.value,
                    "token_id": transaction.token_id,
                    "product_id": transaction.product_id,
                    "wallet_address": transaction.wallet_address,
                    "amount": transaction.amount,
                    "crypto_amount": transaction.crypto_amount,
                    "gas_fee": transaction.gas_fee,
                    "created_at": transaction.created_at,
                    "updated_at": transaction.updated_at
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get transaction status for {transaction_hash}: {e}")
            return None
    
    def get_token_metadata(self, token_id: str, product_id: int) -> Optional[Dict[str, Any]]:
        """Get token metadata"""
        try:
            # Get transaction info
            transaction = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.token_id == token_id,
                TokenTransaction.product_id == product_id
            ).first()
            
            if transaction:
                return {
                    "token_id": token_id,
                    "product_id": product_id,
                    "metadata_uri": transaction.metadata_uri,
                    "acquired_at": transaction.created_at,
                    "transaction_hash": transaction.transaction_hash
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get token metadata for {token_id}: {e}")
            return None
    
    def get_wallet_transactions(
        self,
        wallet_address: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all transactions for wallet"""
        try:
            transactions = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.wallet_address == wallet_address
            ).offset(offset).limit(limit).all()
            
            result = []
            for transaction in transactions:
                result.append({
                    "id": transaction.id,
                    "transaction_hash": transaction.transaction_hash,
                    "token_id": transaction.token_id,
                    "status": transaction.status.value,
                    "amount": transaction.amount,
                    "crypto_amount": transaction.crypto_amount,
                    "crypto_currency": transaction.crypto_currency,
                    "created_at": transaction.created_at
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get wallet transactions for {wallet_address}: {e}")
            return []
    
    def get_product_token_holders(
        self,
        product_id: int,
        tier: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get token holders for a product"""
        try:
            query = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.product_id == product_id,
                TokenTransaction.status == TransactionStatus.CONFIRMED
            )
            
            if tier:
                # This would require joining with Tier table
                # For now, return all holders
                pass
            
            transactions = query.offset(offset).limit(limit).all()
            
            holders = []
            for transaction in transactions:
                if transaction.wallet_address not in [h["wallet_address"] for h in holders]:
                    holders.append({
                        "wallet_address": transaction.wallet_address,
                        "token_id": transaction.token_id,
                        "acquired_at": transaction.created_at,
                        "transaction_hash": transaction.transaction_hash
                    })
            
            return holders
            
        except Exception as e:
            logger.error(f"Failed to get token holders for product {product_id}: {e}")
            return []
    
    def get_token_analytics(self, product_id: int) -> Dict[str, Any]:
        """Get token analytics for a product"""
        try:
            # Total tokens minted
            total_minted = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.product_id == product_id,
                TokenTransaction.status == TransactionStatus.CONFIRMED
            ).count()
            
            # Revenue analytics
            total_revenue = self.db_session.query(TokenTransaction.amount).filter(
                TokenTransaction.product_id == product_id,
                TokenTransaction.status == TransactionStatus.CONFIRMED
            ).all()
            
            total_revenue_amount = sum([float(r[0] or 0) for r in total_revenue])
            
            # Tier distribution
            tier_distribution = {}
            transactions = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.product_id == product_id,
                TokenTransaction.status == TransactionStatus.CONFIRMED
            ).all()
            
            for transaction in transactions:
                tier = "unknown"  # Would get from Tier table
                tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
            
            return {
                "total_tokens_minted": total_minted,
                "total_revenue": total_revenue_amount,
                "tier_distribution": tier_distribution,
                "active_holders": len(set([t.wallet_address for t in transactions]))
            }
            
        except Exception as e:
            logger.error(f"Failed to get token analytics for product {product_id}: {e}")
            return {
                "total_tokens_minted": 0,
                "total_revenue": 0.0,
                "tier_distribution": {},
                "active_holders": 0
            }
    
    def update_transaction_status(
        self,
        transaction_hash: str,
        status: str,
        block_number: int = None,
        gas_fee: float = None
    ) -> bool:
        """Update transaction status"""
        try:
            transaction = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.transaction_hash == transaction_hash
            ).first()
            
            if transaction:
                transaction.status = TransactionStatus(status)
                if block_number:
                    transaction.block_number = block_number
                if gas_fee:
                    transaction.gas_fee = gas_fee
                
                self.db_session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update transaction status for {transaction_hash}: {e}")
            self.db_session.rollback()
            return False
