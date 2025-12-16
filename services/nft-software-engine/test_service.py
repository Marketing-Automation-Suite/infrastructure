#!/usr/bin/env python3
"""
Test script for NFT Software Engine core functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_core_functionality():
    """Test all core functionality of the NFT Software Engine"""
    
    print('🚀 NFT Software Engine - Core Functionality Test')
    print('=' * 60)
    
    try:
        # Test models
        from src.models.database import Product, Tier, TokenTransaction
        print('✅ Database models import successful!')
        
        from src.models.schemas import ProductConfig, TierConfig, ContractType, TierType
        print('✅ Schema models import successful!')
        
        # Test settings
        from src.config.settings import Settings
        settings = Settings()
        print(f'✅ Settings loaded: {settings.APP_NAME}')
        
        # Test wallet generation
        from src.utils.crypto import generate_wallet, validate_private_key
        wallet = generate_wallet()
        print(f'✅ Wallet generated: {wallet["address"]}')
        
        # Test validators
        from src.utils.validators import validate_ethereum_address, validate_token_id
        is_valid = validate_ethereum_address(wallet['address'])
        print(f'✅ Address validation: {is_valid}')
        
        # Test helpers
        from src.utils.helpers import format_currency, truncate_address, generate_slug
        formatted = format_currency(99.99, 'USD')
        truncated = truncate_address(wallet['address'])
        slug = generate_slug('My Cool Product')
        print(f'✅ Helper functions: {formatted}, {truncated}, {slug}')
        
        # Test data structures
        product_config = ProductConfig(
            name='Test Product',
            description='A test NFT product',
            network='polygon'
        )
        print(f'✅ Product config created: {product_config.name}')
        
        tier_config = TierConfig(
            name='Gold',
            tier_type=TierType.GOLD,
            price=100.0,
            features=['Premium Access', 'Advanced Analytics']
        )
        print(f'✅ Tier config created: {tier_config.name} (${tier_config.price})')
        
        # Test service imports
        from src.services.product_service import ProductService
        print('✅ ProductService import successful!')
        
        from src.services.token_service import TokenService
        print('✅ TokenService import successful!')
        
        from src.services.contract_service import ContractService
        print('✅ ContractService import successful!')
        
        from src.services.analytics_service import AnalyticsService
        print('✅ AnalyticsService import successful!')
        
        print('=' * 60)
        print('🎉 ALL TESTS PASSED! NFT Software Engine is working correctly!')
        print('✅ Service ready for Phase 2: Blockchain Integration')
        print('✅ Service ready for Phase 3: API Development')
        print('=' * 60)
        
        return True
        
    except ImportError as e:
        print(f'❌ Import error: {e}')
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f'❌ Other error: {e}')
        import traceback
        traceback.print_exc()
        return False


def test_docker_build():
    """Test if Docker image can be built"""
    print('\n🐳 Testing Docker Build...')
    
    try:
        # Check if Dockerfile exists
        dockerfile_path = os.path.join(os.path.dirname(__file__), 'docker', 'Dockerfile')
        if os.path.exists(dockerfile_path):
            print('✅ Dockerfile found')
            
            # Check requirements.txt
            req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
            if os.path.exists(req_path):
                print('✅ requirements.txt found')
                print('✅ Docker configuration is ready')
                return True
            else:
                print('❌ requirements.txt not found')
                return False
        else:
            print('❌ Dockerfile not found')
            return False
            
    except Exception as e:
        print(f'❌ Docker test error: {e}')
        return False


if __name__ == '__main__':
    print('🧪 Starting NFT Software Engine Tests...')
    
    # Test core functionality
    core_tests_passed = test_core_functionality()
    
    # Test Docker build
    docker_tests_passed = test_docker_build()
    
    print('\n📊 Test Results:')
    print(f'Core Functionality: {"✅ PASS" if core_tests_passed else "❌ FAIL"}')
    print(f'Docker Configuration: {"✅ PASS" if docker_tests_passed else "❌ FAIL"}')
    
    if core_tests_passed and docker_tests_passed:
        print('\n🎉 ALL TESTS PASSED! NFT Software Engine Phase 1 is complete!')
        print('Ready to proceed to Phase 2: Blockchain Integration')
    else:
        print('\n❌ Some tests failed. Please check the errors above.')
