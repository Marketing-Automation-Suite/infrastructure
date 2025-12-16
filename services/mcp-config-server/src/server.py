"""
MCP Configuration Server - FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, status, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import logging
import os
from datetime import datetime

from .database.connection import get_db, init_db
from .database.models import ServiceConfiguration, ConnectionTest
from .encryption.credential_manager import get_credential_manager
from .registry.service_registry import get_registry
from .plugin_loader import get_plugin_loader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Configuration Server",
    version="1.0.0",
    description="Service marketplace and configuration system for external marketing services"
)

# CORS configuration - SECURITY FIX
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_str:
    allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]
else:
    # Development fallback - warn but allow
    allowed_origins = ["*"]
    if os.getenv("ENVIRONMENT") == "production":
        logger.error("ALLOWED_ORIGINS must be set in production!")
        raise ValueError("ALLOWED_ORIGINS environment variable must be set in production")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

# API Key Authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    """
    Verify API key for authentication.
    In production, this should integrate with auth-service.
    """
    # Check if authentication is enabled
    if os.getenv("DISABLE_AUTH", "false").lower() == "true":
        logger.warning("Authentication is DISABLED - not recommended for production")
        return True
    
    # Get expected API key from environment
    expected_key = os.getenv("API_KEY")
    if not expected_key:
        if os.getenv("ENVIRONMENT") == "production":
            raise HTTPException(
                status_code=500,
                detail="API_KEY not configured - server misconfiguration"
            )
        # Development mode - allow without key
        logger.warning("API_KEY not set - allowing unauthenticated access (dev only)")
        return True
    
    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API key"
        )
    
    return True

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        init_db()
        logger.info("MCP Configuration Server started")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise


# Request/Response Models
class ServiceConfigurationRequest(BaseModel):
    service_name: str
    credentials: Dict[str, Any]
    settings: Optional[Dict[str, Any]] = None
    config_name: str = "default"


class ServiceUpdateRequest(BaseModel):
    updates: Dict[str, Any]


class MCPResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    next_steps: Optional[List[str]] = None


# Health endpoints
@app.get("/health")
async def health():
    """Basic health check"""
    return {"status": "healthy", "service": "mcp-config-server"}


@app.get("/health/ready")
async def readiness():
    """Readiness probe"""
    return {"status": "ready"}


@app.get("/health/live")
async def liveness():
    """Liveness probe"""
    return {"status": "alive"}


# MCP Tool Endpoints

@app.get("/mcp/marketplace", response_model=MCPResponse)
async def get_marketplace(
    category: Optional[str] = None,
    search: Optional[str] = None,
    _: bool = Depends(verify_api_key)
):
    """Get marketplace of available services"""
    try:
        registry = get_registry()
        services = registry.list_services(category=category, search_query=search)
        
        return MCPResponse(
            success=True,
            data={"services": services, "count": len(services)},
            message=f"Found {len(services)} services"
        )
    except Exception as e:
        logger.error(f"Error getting marketplace: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/mcp/tools/discover_services", response_model=MCPResponse)
async def discover_services(
    category: str = "all",
    _: bool = Depends(verify_api_key)
):
    """Discover available services by category"""
    try:
        registry = get_registry()
        services = registry.list_services(category=category if category != "all" else None)
        
        return MCPResponse(
            success=True,
            data={"services": services},
            message=f"Discovered {len(services)} services"
        )
    except Exception as e:
        logger.error(f"Error discovering services: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/tools/get_service_info", response_model=MCPResponse)
async def get_service_info(
    service_name: str,
    _: bool = Depends(verify_api_key)
):
    """Get detailed information about a service"""
    try:
        registry = get_registry()
        service = registry.get_service(service_name)
        
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service '{service_name}' not found"
            )
        
        return MCPResponse(
            success=True,
            data={"service": service},
            message=f"Service information for {service_name}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/configure_service", response_model=MCPResponse)
async def configure_service(
    request: ServiceConfigurationRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """Configure a service with credentials"""
    try:
        registry = get_registry()
        credential_manager = get_credential_manager()
        plugin_loader = get_plugin_loader()
        
        # Get service definition
        service = registry.get_service(request.service_name)
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service '{request.service_name}' not found"
            )
        
        # Validate required credentials
        required = registry.get_required_credentials(request.service_name)
        missing = [field for field in required if field not in request.credentials]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required credentials: {', '.join(missing)}"
            )
        
        # Test connection before saving
        connector = plugin_loader.get_connector(request.service_name)
        if not connector:
            raise HTTPException(
                status_code=500,
                detail=f"Connector for {request.service_name} not found"
            )
        
        test_result = connector.test_connection(request.credentials)
        
        # Encrypt credentials
        encrypted_credentials = credential_manager.encrypt_credentials(request.credentials)
        
        # Save configuration
        config = ServiceConfiguration(
            service_id=request.service_name,
            config_name=request.config_name,
            encrypted_credentials=encrypted_credentials,
            settings=request.settings,
            status="active" if test_result.get("status") == "success" else "failed",
            last_tested_at=datetime.utcnow(),
            last_test_result=test_result
        )
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        # Save connection test
        if test_result:
            test_record = ConnectionTest(
                configuration_id=config.id,
                test_status=test_result.get("status", "unknown"),
                test_result=test_result,
                error_message=test_result.get("error"),
                test_duration_ms=test_result.get("duration_ms", 0)
            )
            db.add(test_record)
            db.commit()
        
        return MCPResponse(
            success=True,
            data={
                "configuration_id": config.id,
                "service_name": request.service_name,
                "status": config.status,
                "test_result": test_result
            },
            message="Service configured successfully" if test_result.get("status") == "success" else "Service configured but connection test failed",
            next_steps=["Test connection", "Create workflow"] if test_result.get("status") == "success" else ["Check credentials", "Retry connection test"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring service: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/test_service_connection", response_model=MCPResponse)
async def test_service_connection(
    service_name: str,
    config_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """Test connection to a configured service"""
    try:
        registry = get_registry()
        credential_manager = get_credential_manager()
        plugin_loader = get_plugin_loader()
        
        # Get configuration
        if config_id:
            config = db.query(ServiceConfiguration).filter(
                ServiceConfiguration.id == config_id
            ).first()
        else:
            config = db.query(ServiceConfiguration).filter(
                ServiceConfiguration.service_id == service_name,
                ServiceConfiguration.status == "active"
            ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"Configuration for '{service_name}' not found"
            )
        
        # Decrypt credentials
        credentials = credential_manager.decrypt_credentials(config.encrypted_credentials)
        
        # Get connector and test
        connector = plugin_loader.get_connector(service_name)
        if not connector:
            raise HTTPException(
                status_code=500,
                detail=f"Connector for {service_name} not found"
            )
        
        start_time = datetime.utcnow()
        test_result = connector.test_connection(credentials)
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # Update configuration
        config.last_tested_at = datetime.utcnow()
        config.last_test_result = test_result
        config.status = "active" if test_result.get("status") == "success" else "failed"
        db.commit()
        
        # Save test record
        test_record = ConnectionTest(
            configuration_id=config.id,
            test_status=test_result.get("status", "unknown"),
            test_result=test_result,
            error_message=test_result.get("error"),
            test_duration_ms=duration_ms
        )
        db.add(test_record)
        db.commit()
        
        return MCPResponse(
            success=test_result.get("status") == "success",
            data={"test_result": test_result, "duration_ms": duration_ms},
            message=test_result.get("message", "Connection test completed")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing service connection: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/tools/list_configured_services", response_model=MCPResponse)
async def list_configured_services(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """List all configured services"""
    try:
        configs = db.query(ServiceConfiguration).all()
        
        services = []
        for config in configs:
            services.append({
                "id": config.id,
                "service_id": config.service_id,
                "config_name": config.config_name,
                "status": config.status,
                "last_tested_at": config.last_tested_at,
                "created_at": config.created_at.isoformat() if config.created_at else None
            })
        
        return MCPResponse(
            success=True,
            data={"services": services, "count": len(services)},
            message=f"Found {len(services)} configured services"
        )
    except Exception as e:
        logger.error(f"Error listing configured services: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp/tools/update_service_config", response_model=MCPResponse)
async def update_service_config(
    service_name: str,
    request: ServiceUpdateRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """Update service configuration"""
    try:
        credential_manager = get_credential_manager()
        
        # Get configuration
        config = db.query(ServiceConfiguration).filter(
            ServiceConfiguration.service_id == service_name
        ).first()
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"Configuration for '{service_name}' not found"
            )
        
        # Update credentials if provided
        if "credentials" in request.updates:
            encrypted = credential_manager.encrypt_credentials(request.updates["credentials"])
            config.encrypted_credentials = encrypted
        
        # Update settings if provided
        if "settings" in request.updates:
            config.settings = request.updates["settings"]
        
        db.commit()
        db.refresh(config)
        
        return MCPResponse(
            success=True,
            data={"configuration_id": config.id},
            message="Configuration updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/tools/get_configuration_guide", response_model=MCPResponse)
async def get_configuration_guide(
    service_name: str,
    _: bool = Depends(verify_api_key)
):
    """Get step-by-step configuration guide for a service"""
    try:
        registry = get_registry()
        service = registry.get_service(service_name)
        
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service '{service_name}' not found"
            )
        
        guide = {
            "service_name": service_name,
            "name": service.get("name"),
            "configuration_steps": registry.get_configuration_steps(service_name),
            "required_credentials": registry.get_required_credentials(service_name),
            "optional_credentials": registry.get_optional_credentials(service_name),
            "capabilities": registry.get_service_capabilities(service_name)
        }
        
        return MCPResponse(
            success=True,
            data={"guide": guide},
            message=f"Configuration guide for {service_name}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting configuration guide: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mcp/tools/search_marketplace", response_model=MCPResponse)
async def search_marketplace(
    use_case: Optional[str] = None,
    integration_type: Optional[str] = None,
    category: Optional[str] = None,
    _: bool = Depends(verify_api_key)
):
    """Search marketplace for services"""
    try:
        registry = get_registry()
        services = registry.search_marketplace(
            use_case=use_case,
            integration_type=integration_type,
            category=category
        )
        
        return MCPResponse(
            success=True,
            data={"services": services, "count": len(services)},
            message=f"Found {len(services)} matching services"
        )
    except Exception as e:
        logger.error(f"Error searching marketplace: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

