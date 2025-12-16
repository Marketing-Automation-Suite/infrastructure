"""
Token economy analytics service
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from ..models.database import Product, TokenTransaction, TransactionStatus, Tier
from ..models.schemas import AnalyticsResponse
from ..config.settings import settings

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for token economy analytics"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def get_global_analytics(self) -> AnalyticsResponse:
        """Get global NFT engine analytics"""
        try:
            # Total products
            total_products = self.db_session.query(Product).count()
            
            # Total tokens minted
            total_tokens_minted = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.status == TransactionStatus.CONFIRMED
            ).count()
            
            # Total revenue
            total_revenue_result = self.db_session.query(
                func.sum(TokenTransaction.amount)
            ).filter(
                TokenTransaction.status == TransactionStatus.CONFIRMED,
                TokenTransaction.amount.isnot(None)
            ).first()
            
            total_revenue = float(total_revenue_result[0] or 0)
            
            # Active products (with transactions in last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            active_products = self.db_session.query(TokenTransaction.product_id).filter(
                TokenTransaction.status == TransactionStatus.CONFIRMED,
                TokenTransaction.created_at >= thirty_days_ago
            ).distinct().count()
            
            # Top products by revenue
            top_products = self._get_top_products_by_revenue()
            
            # Transaction volume by network
            transaction_volume = self._get_transaction_volume_by_network()
            
            # Network distribution
            network_distribution = self._get_network_distribution()
            
            return AnalyticsResponse(
                total_products=total_products,
                total_tokens_minted=total_tokens_minted,
                total_revenue=total_revenue,
                active_products=active_products,
                top_products=top_products,
                transaction_volume=transaction_volume,
                network_distribution=network_distribution
            )
            
        except Exception as e:
            logger.error(f"Failed to get global analytics: {e}")
            return AnalyticsResponse(
                total_products=0,
                total_tokens_minted=0,
                total_revenue=0.0,
                active_products=0,
                top_products=[],
                transaction_volume={},
                network_distribution={}
            )
    
    def get_product_analytics(self, product_id: int) -> Dict[str, Any]:
        """Get analytics for specific product"""
        try:
            # Get product info
            product = self.db_session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return {"error": "Product not found"}
            
            # Basic metrics
            total_transactions = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.product_id == product_id
            ).count()
            
            confirmed_transactions = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.product_id == product_id,
                TokenTransaction.status == TransactionStatus.CONFIRMED
            ).count()
            
            pending_transactions = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.product_id == product_id,
                TokenTransaction.status == TransactionStatus.PENDING
            ).count()
            
            # Revenue metrics
            revenue_result = self.db_session.query(
                func.sum(TokenTransaction.amount)
            ).filter(
                TokenTransaction.product_id == product_id,
                TokenTransaction.status == TransactionStatus.CONFIRMED,
                TokenTransaction.amount.isnot(None)
            ).first()
            
            total_revenue = float(revenue_result[0] or 0)
            
            # Token analytics
            unique_holders = self.db_session.query(TokenTransaction.wallet_address).filter(
                TokenTransaction.product_id == product_id,
                TokenTransaction.status == TransactionStatus.CONFIRMED
            ).distinct().count()
            
            # Tier distribution
            tier_distribution = self._get_tier_distribution(product_id)
            
            # Transaction trends (last 30 days)
            transaction_trends = self._get_transaction_trends(product_id)
            
            # Network distribution
            network_dist = self.db_session.query(Product.network).filter(
                Product.id == product_id
            ).first()
            
            return {
                "product_id": product_id,
                "product_name": product.name,
                "total_transactions": total_transactions,
                "confirmed_transactions": confirmed_transactions,
                "pending_transactions": pending_transactions,
                "success_rate": (confirmed_transactions / total_transactions * 100) if total_transactions > 0 else 0,
                "total_revenue": total_revenue,
                "unique_holders": unique_holders,
                "tier_distribution": tier_distribution,
                "transaction_trends": transaction_trends,
                "network": network_dist[0] if network_dist else "unknown",
                "contract_address": product.contract_address,
                "contract_type": product.contract_type.value,
                "created_at": product.created_at
            }
            
        except Exception as e:
            logger.error(f"Failed to get product analytics for {product_id}: {e}")
            return {"error": str(e)}
    
    def get_network_analytics(self, network: str) -> Dict[str, Any]:
        """Get analytics for specific network"""
        try:
            # Products on this network
            products = self.db_session.query(Product).filter(Product.network == network).all()
            product_ids = [p.id for p in products]
            
            if not product_ids:
                return {
                    "network": network,
                    "products": 0,
                    "total_transactions": 0,
                    "total_revenue": 0.0,
                    "total_holders": 0
                }
            
            # Transactions for products on this network
            total_transactions = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.product_id.in_(product_ids)
            ).count()
            
            confirmed_transactions = self.db_session.query(TokenTransaction).filter(
                TokenTransaction.product_id.in_(product_ids),
                TokenTransaction.status == TransactionStatus.CONFIRMED
            ).count()
            
            # Revenue
            revenue_result = self.db_session.query(
                func.sum(TokenTransaction.amount)
            ).filter(
                TokenTransaction.product_id.in_(product_ids),
                TokenTransaction.status == TransactionStatus.CONFIRMED,
                TokenTransaction.amount.isnot(None)
            ).first()
            
            total_revenue = float(revenue_result[0] or 0)
            
            # Unique holders
            unique_holders = self.db_session.query(TokenTransaction.wallet_address).filter(
                TokenTransaction.product_id.in_(product_ids),
                TokenTransaction.status == TransactionStatus.CONFIRMED
            ).distinct().count()
            
            # Top products on this network
            top_products = self._get_top_products_by_revenue(network=network)
            
            return {
                "network": network,
                "products": len(products),
                "total_transactions": total_transactions,
                "confirmed_transactions": confirmed_transactions,
                "total_revenue": total_revenue,
                "total_holders": unique_holders,
                "success_rate": (confirmed_transactions / total_transactions * 100) if total_transactions > 0 else 0,
                "top_products": top_products
            }
            
        except Exception as e:
            logger.error(f"Failed to get network analytics for {network}: {e}")
            return {"error": str(e)}
    
    def get_token_metrics(self, token_id: str = None, contract_address: str = None) -> Dict[str, Any]:
        """Get metrics for specific token or contract"""
        try:
            if token_id:
                # Single token analytics
                transaction = self.db_session.query(TokenTransaction).filter(
                    TokenTransaction.token_id == token_id
                ).first()
                
                if not transaction:
                    return {"error": "Token not found"}
                
                return {
                    "token_id": token_id,
                    "product_id": transaction.product_id,
                    "wallet_address": transaction.wallet_address,
                    "acquired_at": transaction.created_at,
                    "transaction_hash": transaction.transaction_hash,
                    "status": transaction.status.value,
                    "amount_paid": transaction.amount,
                    "gas_fee": transaction.gas_fee
                }
            
            elif contract_address:
                # Contract-level analytics
                product = self.db_session.query(Product).filter(
                    Product.contract_address == contract_address
                ).first()
                
                if not product:
                    return {"error": "Contract not found"}
                
                return self.get_product_analytics(product.id)
            
            else:
                return {"error": "Either token_id or contract_address required"}
                
        except Exception as e:
            logger.error(f"Failed to get token metrics: {e}")
            return {"error": str(e)}
    
    def _get_top_products_by_revenue(self, limit: int = 10, network: str = None) -> List[Dict[str, Any]]:
        """Get top products by revenue"""
        try:
            query = self.db_session.query(
                TokenTransaction.product_id,
                func.sum(TokenTransaction.amount).label('total_revenue'),
                func.count(TokenTransaction.id).label('transaction_count')
            ).filter(
                TokenTransaction.status == TransactionStatus.CONFIRMED,
                TokenTransaction.amount.isnot(None)
            ).group_by(TokenTransaction.product_id).order_by(
                desc('total_revenue')
            ).limit(limit)
            
            if network:
                query = query.join(Product).filter(Product.network == network)
            
            results = query.all()
            
            top_products = []
            for result in results:
                product = self.db_session.query(Product).filter(
                    Product.id == result.product_id
                ).first()
                
                top_products.append({
                    "product_id": result.product_id,
                    "product_name": product.name if product else "Unknown",
                    "total_revenue": float(result.total_revenue or 0),
                    "transaction_count": result.transaction_count,
                    "network": product.network if product else "unknown"
                })
            
            return top_products
            
        except Exception as e:
            logger.error(f"Failed to get top products: {e}")
            return []
    
    def _get_transaction_volume_by_network(self) -> Dict[str, float]:
        """Get transaction volume by network"""
        try:
            results = self.db_session.query(
                Product.network,
                func.sum(TokenTransaction.amount)
            ).join(
                TokenTransaction
            ).filter(
                TokenTransaction.status == TransactionStatus.CONFIRMED,
                TokenTransaction.amount.isnot(None)
            ).group_by(Product.network).all()
            
            return {network: float(amount or 0) for network, amount in results}
            
        except Exception as e:
            logger.error(f"Failed to get transaction volume by network: {e}")
            return {}
    
    def _get_network_distribution(self) -> Dict[str, int]:
        """Get product distribution by network"""
        try:
            results = self.db_session.query(
                Product.network,
                func.count(Product.id)
            ).group_by(Product.network).all()
            
            return {network: count for network, count in results}
            
        except Exception as e:
            logger.error(f"Failed to get network distribution: {e}")
            return {}
    
    def _get_tier_distribution(self, product_id: int) -> Dict[str, int]:
        """Get transaction distribution by tier"""
        try:
            results = self.db_session.query(
                Tier.name,
                func.count(TokenTransaction.id)
            ).join(
                TokenTransaction
            ).filter(
                TokenTransaction.product_id == product_id,
                TokenTransaction.status == TransactionStatus.CONFIRMED
            ).group_by(Tier.name).all()
            
            return {tier_name: count for tier_name, count in results}
            
        except Exception as e:
            logger.error(f"Failed to get tier distribution: {e}")
            return {}
    
    def _get_transaction_trends(self, product_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """Get transaction trends for last N days"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            results = self.db_session.query(
                func.date(TokenTransaction.created_at).label('date'),
                func.count(TokenTransaction.id).label('count'),
                func.sum(TokenTransaction.amount).label('revenue')
            ).filter(
                TokenTransaction.product_id == product_id,
                TokenTransaction.created_at >= start_date
            ).group_by(
                func.date(TokenTransaction.created_at)
            ).order_by('date').all()
            
            trends = []
            for result in results:
                trends.append({
                    "date": result.date.isoformat(),
                    "transactions": result.count,
                    "revenue": float(result.revenue or 0)
                })
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to get transaction trends: {e}")
            return []
