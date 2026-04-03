"""
General utility functions and helpers
"""

import re
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json


def sanitize_text(text: str) -> str:
    """Sanitize text content for safe processing"""
    
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove potentially problematic characters
    text = re.sub(r'[^\w\s\-\.\,\!\?\;\:\(\)\[\]\{\}\/\\@#\$%\^&\*\+\=\|\<\>]', '', text)
    
    return text.strip()


def generate_id(prefix: str = "", data: Optional[Dict[str, Any]] = None) -> str:
    """Generate a consistent ID from data"""
    
    if data:
        # Create hash from data
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        hash_hex = hash_obj.hexdigest()[:8]
        
        if prefix:
            return f"{prefix}_{hash_hex}"
        return hash_hex
    
    # Generate timestamp-based ID
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    if prefix:
        return f"{prefix}_{timestamp}"
    return timestamp


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format"""
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def parse_time_range(time_range: str) -> Dict[str, datetime]:
    """Parse time range string into start and end datetime"""
    
    now = datetime.utcnow()
    
    if time_range.endswith("m"):
        minutes = int(time_range[:-1])
        start = now - timedelta(minutes=minutes)
    elif time_range.endswith("h"):
        hours = int(time_range[:-1])
        start = now - timedelta(hours=hours)
    elif time_range.endswith("d"):
        days = int(time_range[:-1])
        start = now - timedelta(days=days)
    else:
        # Default to 1 hour
        start = now - timedelta(hours=1)
    
    return {"start": start, "end": now}


def extract_error_info(log_message: str) -> Dict[str, Any]:
    """Extract structured error information from log messages"""
    
    error_info = {
        "error_type": None,
        "error_message": None,
        "stack_trace": None,
        "service": None,
        "timestamp": None
    }
    
    # Extract error type (common patterns)
    error_types = [
        r"(\w*Error|Exception|Throwable)",
        r"HTTP\s+(\d{3})",
        r"Status:\s+(\d{3})"
    ]
    
    for pattern in error_types:
        match = re.search(pattern, log_message, re.IGNORECASE)
        if match:
            error_info["error_type"] = match.group(1)
            break
    
    # Extract error message
    message_patterns = [
        r"(?:Error|Exception|Throwable):\s*(.+?)(?:\n|$)",
        r"Message:\s*(.+?)(?:\n|$)",
        r"Description:\s*(.+?)(?:\n|$)"
    ]
    
    for pattern in message_patterns:
        match = re.search(pattern, log_message, re.IGNORECASE)
        if match:
            error_info["error_message"] = match.group(1).strip()
            break
    
    # Extract stack trace (simplified)
    stack_pattern = r"(?:at\s+|File\s+[\"'])(.+?)(?:\n|$)"
    stack_matches = re.findall(stack_pattern, log_message)
    if stack_matches:
        error_info["stack_trace"] = stack_matches[:5]  # Limit to first 5 lines
    
    # Extract service name (common patterns)
    service_patterns = [
        r"\[([a-zA-Z0-9\-_]+)\]",
        r"service:\s*([a-zA-Z0-9\-_]+)",
        r"component:\s*([a-zA-Z0-9\-_]+)"
    ]
    
    for pattern in service_patterns:
        match = re.search(pattern, log_message)
        if match:
            error_info["service"] = match.group(1)
            break
    
    # Extract timestamp (ISO format)
    timestamp_pattern = r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})"
    match = re.search(timestamp_pattern, log_message)
    if match:
        try:
            timestamp_str = match.group(1).replace(' ', 'T')
            error_info["timestamp"] = datetime.fromisoformat(timestamp_str)
        except:
            pass
    
    return error_info


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size"""
    
    chunks = []
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        chunks.append(chunk)
    
    return chunks


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two dictionaries recursively"""
    
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def validate_email(email: str) -> bool:
    """Validate email format"""
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text)


def is_json_serializable(obj: Any) -> bool:
    """Check if object is JSON serializable"""
    
    try:
        json.dumps(obj)
        return True
    except (TypeError, ValueError):
        return False


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """Safely load JSON string"""
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default
