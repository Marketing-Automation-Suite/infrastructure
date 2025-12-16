"""
Helper functions for NFT Software Engine
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json
from decimal import Decimal


def format_token_id(token_id: Any) -> str:
    """Format token ID for display"""
    if isinstance(token_id, int):
        return str(token_id)
    elif isinstance(token_id, str):
        return token_id
    else:
        return str(token_id)


def format_wei_to_ether(wei_amount: int) -> str:
    """Convert wei to ether and format"""
    ether_amount = wei_amount / (10 ** 18)
    return f"{ether_amount:.6f}"


def format_gwei_to_ether(gwei_amount: int) -> str:
    """Convert gwei to ether and format"""
    ether_amount = gwei_amount / (10 ** 9)
    return f"{ether_amount:.6f}"


def calculate_gas_estimate(gas_used: int, gas_price_gwei: int) -> int:
    """Calculate total gas cost in wei"""
    return gas_used * (gas_price_gwei * 10 ** 9)


def calculate_percentage(value: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0.0
    return (value / total) * 100


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "ETH":
        return f"{amount:.6f} ETH"
    elif currency == "MATIC":
        return f"{amount:.6f} MATIC"
    else:
        return f"{amount:.2f} {currency}"


def format_percentage(percentage: float) -> str:
    """Format percentage for display"""
    return f"{percentage:.2f}%"


def normalize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize NFT metadata"""
    normalized = {}
    
    # Standard NFT metadata fields
    normalized["name"] = metadata.get("name", "")
    normalized["description"] = metadata.get("description", "")
    normalized["image"] = metadata.get("image", "")
    normalized["external_url"] = metadata.get("external_url", "")
    
    # Attributes
    if "attributes" in metadata:
        normalized["attributes"] = metadata["attributes"]
    else:
        normalized["attributes"] = []
    
    # Custom fields
    for key, value in metadata.items():
        if key not in ["name", "description", "image", "external_url", "attributes"]:
            normalized[key] = value
    
    return normalized


def paginate_results(items: List[Any], page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """Paginate a list of items"""
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        "items": items[start:end],
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page,
        "per_page": per_page,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


def validate_json_structure(data: str) -> Optional[Dict[str, Any]]:
    """Validate and parse JSON string"""
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None


def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp for display"""
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


def truncate_address(address: str, length: int = 6) -> str:
    """Truncate address for display"""
    if len(address) <= length * 2 + 3:
        return address
    
    return f"{address[:length]}...{address[-length:]}"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"


def validate_url_format(url: str) -> bool:
    """Validate URL format (basic check)"""
    if not url:
        return False
    
    return (
        url.startswith(('http://', 'https://')) and
        '.' in url and
        len(url) > 10
    )


def clean_whitespace(text: str) -> str:
    """Clean whitespace from text"""
    if not text:
        return ""
    
    return ' '.join(text.split())


def convert_to_decimal(value: Any) -> Optional[Decimal]:
    """Convert value to Decimal"""
    try:
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    except (ValueError, TypeError):
        return None


def format_decimal(decimal_value: Decimal, places: int = 6) -> str:
    """Format decimal value"""
    return f"{decimal_value:.{places}f}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    if not filename:
        return ""
    
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250-len(ext)] + ('.' + ext if ext else '')
    
    return filename


def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    if not text:
        return ""
    
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().replace(' ', '-')
    
    # Remove special characters
    import re
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    
    # Remove multiple consecutive hyphens
    slug = re.sub(r'\-+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    return slug


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, str]:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, str(v)))
    return dict(items)
