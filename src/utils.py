"""
Utility functions for the application
"""
import json
from uuid import UUID
from typing import Any, Dict, List, Union
from fastapi.encoders import jsonable_encoder

class UUIDEncoder(json.JSONEncoder):
    """JSON encoder that can handle UUID objects"""
    def default(self, obj):
        if isinstance(obj, UUID):
            # Convert UUID to string
            return str(obj)
        return super().default(obj)

def serialize_data(data: Any) -> Any:
    """
    Serialize data to ensure it's JSON compatible.
    Handles UUID objects and other non-serializable types.
    
    Args:
        data: Data to serialize
        
    Returns:
        JSON-serializable data
    """
    return jsonable_encoder(data)

def json_dumps(data: Any) -> str:
    """
    Convert data to JSON string with UUID handling.
    
    Args:
        data: Data to serialize to JSON
        
    Returns:
        JSON string
    """
    return json.dumps(data, cls=UUIDEncoder)

def is_datastar(req):
    """
    Check if the request is from DataStar.
    
    Args:
        req: The request object
        
    Returns:
        True if the request is from DataStar, False otherwise
    """
    return req.headers.get("Datastar-Request") == "true"