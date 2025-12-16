"""
Smart contract management service
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ..models.database import NFTContract, ContractType, Product
from ..models.schemas import SmartContractDeployment, ContractResponse
from ..core.contracts import ContractInterface, TieredNFTContract
from ..config.settings import settings

logger = logging.getLogger(__name__)


class ContractService:
    """Service for smart contract management"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def deploy_contract(
        self,
        product_id: int,
        contract_type: ContractType,
        network: str,
        base_uri: str = None
    ) -> SmartContractDeployment:
        """Deploy smart contract for product"""
        try:
            # Get product info
            product = self.db_session.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise ValueError("Product not found")
            
            # Use base URI from settings if not provided
            if not base_uri:
                base_uri = f"{settings.NFT_BASE_URI}{product_id}/"
            
            # Deploy contract (placeholder implementation)
            # In real implementation, this would compile and deploy the contract
            contract_address = self._simulate_contract_deployment(product_id, contract_type, network)
            
            # Create contract record
            contract = NFTContract(
                product_id=product_id,
                contract_address=contract_address,
                contract_type=contract_type,
                network=network,
                name=f"{product.name} NFT",
                symbol=f"{product.name.upper()[:4]}NFT",
                base_uri=base_uri,
                verified=False,
                active=True
            )
            
            self.db_session.add(contract)
            self.db_session.flush()
            
            # Update product with contract address
            product.contract_address = contract_address
            product.base_uri = base_uri
            self.db_session.commit()
            
            logger.info(f"Contract deployed: {contract_address} for product {product_id}")
            
            return SmartContractDeployment(
                contract_address=contract_address,
                network=network,
                transaction_hash="0x1234567890abcdef",  # Placeholder
                block_number=12345678,  # Placeholder
                deployed_at=contract.created_at,
                gas_used=500000,  # Placeholder
                deployment_cost=0.1  # Placeholder
            )
            
        except Exception as e:
            logger.error(f"Contract deployment failed: {e}")
            self.db_session.rollback()
            raise
    
    def verify_contract(self, contract_address: str) -> bool:
        """Verify deployed contract on blockchain explorer"""
        try:
            contract = self.db_session.query(NFTContract).filter(
                NFTContract.contract_address == contract_address
            ).first()
            
            if not contract:
                return False
            
            # Simulate contract verification
            # In real implementation, this would verify on Etherscan/Polygonscan
            contract.verified = True
            self.db_session.commit()
            
            logger.info(f"Contract verified: {contract_address}")
            
            return True
            
        except Exception as e:
            logger.error(f"Contract verification failed for {contract_address}: {e}")
            return False
    
    def get_contract(self, contract_address: str) -> Optional[ContractResponse]:
        """Get contract information"""
        try:
            contract = self.db_session.query(NFTContract).filter(
                NFTContract.contract_address == contract_address
            ).first()
            
            if contract:
                return self._to_contract_response(contract)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get contract {contract_address}: {e}")
            return None
    
    def get_product_contracts(self, product_id: int) -> List[ContractResponse]:
        """Get all contracts for a product"""
        try:
            contracts = self.db_session.query(NFTContract).filter(
                NFTContract.product_id == product_id
            ).all()
            
            return [self._to_contract_response(contract) for contract in contracts]
            
        except Exception as e:
            logger.error(f"Failed to get contracts for product {product_id}: {e}")
            return []
    
    def update_contract_config(
        self,
        contract_address: str,
        config_updates: Dict[str, Any]
    ) -> Optional[ContractResponse]:
        """Update contract configuration"""
        try:
            contract = self.db_session.query(NFTContract).filter(
                NFTContract.contract_address == contract_address
            ).first()
            
            if not contract:
                return None
            
            # Update fields
            for field, value in config_updates.items():
                if hasattr(contract, field):
                    setattr(contract, field, value)
            
            self.db_session.commit()
            
            logger.info(f"Contract config updated: {contract_address}")
            
            return self._to_contract_response(contract)
            
        except Exception as e:
            logger.error(f"Failed to update contract config for {contract_address}: {e}")
            self.db_session.rollback()
            return None
    
    def get_contract_status(self, contract_address: str) -> Dict[str, Any]:
        """Get deployment and verification status"""
        try:
            contract = self.db_session.query(NFTContract).filter(
                NFTContract.contract_address == contract_address
            ).first()
            
            if not contract:
                return {"error": "Contract not found"}
            
            # Simulate blockchain status check
            # In real implementation, this would check contract on blockchain
            is_deployed = True
            is_verified = contract.verified
            
            return {
                "contract_address": contract_address,
                "is_deployed": is_deployed,
                "is_verified": is_verified,
                "network": contract.network,
                "contract_type": contract.contract_type.value,
                "deployment_block": contract.block_number,
                "total_supply": contract.total_supply or 0,
                "last_activity": contract.updated_at
            }
            
        except Exception as e:
            logger.error(f"Failed to get contract status for {contract_address}: {e}")
            return {"error": str(e)}
    
    def deactivate_contract(self, contract_address: str) -> bool:
        """Deactivate a contract"""
        try:
            contract = self.db_session.query(NFTContract).filter(
                NFTContract.contract_address == contract_address
            ).first()
            
            if not contract:
                return False
            
            contract.active = False
            self.db_session.commit()
            
            logger.info(f"Contract deactivated: {contract_address}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deactivate contract {contract_address}: {e}")
            self.db_session.rollback()
            return False
    
    def get_contracts_by_network(self, network: str) -> List[ContractResponse]:
        """Get contracts by blockchain network"""
        try:
            contracts = self.db_session.query(NFTContract).filter(
                NFTContract.network == network,
                NFTContract.active == True
            ).all()
            
            return [self._to_contract_response(contract) for contract in contracts]
            
        except Exception as e:
            logger.error(f"Failed to get contracts for network {network}: {e}")
            return []
    
    def _simulate_contract_deployment(
        self,
        product_id: int,
        contract_type: ContractType,
        network: str
    ) -> str:
        """Simulate contract deployment (placeholder for actual deployment)"""
        # In real implementation, this would:
        # 1. Compile smart contract code
        # 2. Deploy to blockchain
        # 3. Return actual contract address
        
        # For now, generate a placeholder address
        import hashlib
        contract_hash = hashlib.sha256(
            f"{product_id}-{contract_type.value}-{network}".encode()
        ).hexdigest()[:40]
        
        return f"0x{contract_hash}"
    
    def _to_contract_response(self, contract: NFTContract) -> ContractResponse:
        """Convert NFTContract model to ContractResponse"""
        return ContractResponse(
            id=contract.id,
            product_id=contract.product_id,
            contract_address=contract.contract_address,
            contract_type=contract.contract_type,
            network=contract.network,
            transaction_hash=contract.transaction_hash,
            block_number=contract.block_number,
            name=contract.name,
            symbol=contract.symbol,
            total_supply=contract.total_supply,
            verified=contract.verified,
            active=contract.active,
            created_at=contract.created_at
        )
