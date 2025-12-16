"""
Product lifecycle management service
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..models.database import Product, Tier, ContractType, TierType
from ..models.schemas import ProductCreate, TierCreate, ProductResponse, TierResponse
from ..config.settings import settings

logger = logging.getLogger(__name__)


class ProductService:
    """Service for product lifecycle management"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create_product(
        self,
        product_data: ProductCreate,
        tier_data: List[TierCreate]
    ) -> ProductResponse:
        """Create a new product with tiers"""
        try:
            # Create product
            product = Product(
                name=product_data.name,
                description=product_data.description,
                website=product_data.website,
                logo_url=product_data.logo_url,
                network=product_data.network,
                currency=product_data.currency,
                contract_type=product_data.contract_type,
                base_uri=product_data.base_uri,
                royalty_fee=product_data.royalty_fee,
                transfer_enabled=product_data.transfer_enabled,
                features=product_data.features
            )
            
            self.db_session.add(product)
            self.db_session.flush()  # Get product ID
            
            # Create tiers
            for tier_info in tier_data:
                tier = Tier(
                    product_id=product.id,
                    name=tier_info.name,
                    tier_type=tier_info.tier_type,
                    price=tier_info.price,
                    max_supply=tier_info.max_supply,
                    features=tier_info.features,
                    limits=tier_info.limits
                )
                self.db_session.add(tier)
            
            self.db_session.commit()
            
            logger.info(f"Product created: {product.name} (ID: {product.id})")
            
            return self._to_product_response(product)
            
        except Exception as e:
            logger.error(f"Failed to create product: {e}")
            self.db_session.rollback()
            raise
    
    def get_product(self, product_id: int) -> Optional[ProductResponse]:
        """Get product by ID"""
        try:
            product = self.db_session.query(Product).filter(Product.id == product_id).first()
            if product:
                return self._to_product_response(product)
            return None
        except Exception as e:
            logger.error(f"Failed to get product {product_id}: {e}")
            return None
    
    def list_products(self, limit: int = 100, offset: int = 0) -> List[ProductResponse]:
        """List all products"""
        try:
            products = self.db_session.query(Product).offset(offset).limit(limit).all()
            return [self._to_product_response(product) for product in products]
        except Exception as e:
            logger.error(f"Failed to list products: {e}")
            return []
    
    def update_product(
        self,
        product_id: int,
        product_data: Dict[str, Any]
    ) -> Optional[ProductResponse]:
        """Update product"""
        try:
            product = self.db_session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return None
            
            # Update fields
            for field, value in product_data.items():
                if hasattr(product, field):
                    setattr(product, field, value)
            
            product.updated_at = None  # Let SQLAlchemy handle this
            
            self.db_session.commit()
            
            logger.info(f"Product updated: {product.name} (ID: {product.id})")
            
            return self._to_product_response(product)
            
        except Exception as e:
            logger.error(f"Failed to update product {product_id}: {e}")
            self.db_session.rollback()
            return None
    
    def delete_product(self, product_id: int) -> bool:
        """Delete product"""
        try:
            product = self.db_session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return False
            
            self.db_session.delete(product)
            self.db_session.commit()
            
            logger.info(f"Product deleted: {product_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete product {product_id}: {e}")
            self.db_session.rollback()
            return False
    
    def get_product_tiers(self, product_id: int) -> List[TierResponse]:
        """Get all tiers for a product"""
        try:
            tiers = self.db_session.query(Tier).filter(Tier.product_id == product_id).all()
            return [self._to_tier_response(tier) for tier in tiers]
        except Exception as e:
            logger.error(f"Failed to get tiers for product {product_id}: {e}")
            return []
    
    def get_tier_by_name(self, product_id: int, tier_name: str) -> Optional[TierResponse]:
        """Get specific tier by name"""
        try:
            tier = self.db_session.query(Tier).filter(
                Tier.product_id == product_id,
                Tier.name == tier_name
            ).first()
            
            if tier:
                return self._to_tier_response(tier)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get tier {tier_name} for product {product_id}: {e}")
            return None
    
    def get_products_by_network(self, network: str) -> List[ProductResponse]:
        """Get products by blockchain network"""
        try:
            products = self.db_session.query(Product).filter(Product.network == network).all()
            return [self._to_product_response(product) for product in products]
        except Exception as e:
            logger.error(f"Failed to get products for network {network}: {e}")
            return []
    
    def update_contract_address(self, product_id: int, contract_address: str) -> bool:
        """Update product's contract address"""
        try:
            product = self.db_session.query(Product).filter(Product.id == product_id).first()
            if not product:
                return False
            
            product.contract_address = contract_address
            self.db_session.commit()
            
            logger.info(f"Contract address updated for product {product_id}: {contract_address}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update contract address for product {product_id}: {e}")
            self.db_session.rollback()
            return False
    
    def _to_product_response(self, product: Product) -> ProductResponse:
        """Convert Product model to ProductResponse"""
        return ProductResponse(
            id=product.id,
            name=product.name,
            description=product.description,
            website=product.website,
            logo_url=product.logo_url,
            network=product.network,
            currency=product.currency,
            contract_address=product.contract_address,
            contract_type=product.contract_type,
            base_uri=product.base_uri,
            royalty_fee=product.royalty_fee,
            transfer_enabled=product.transfer_enabled,
            features=product.features or {},
            created_at=product.created_at,
            updated_at=product.updated_at
        )
    
    def _to_tier_response(self, tier: Tier) -> TierResponse:
        """Convert Tier model to TierResponse"""
        return TierResponse(
            id=tier.id,
            product_id=tier.product_id,
            name=tier.name,
            tier_type=tier.tier_type,
            price=tier.price,
            max_supply=tier.max_supply,
            features=tier.features or [],
            limits=tier.limits or {},
            created_at=tier.created_at
        )
