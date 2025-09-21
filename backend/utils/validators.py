"""
Input validation utilities
"""
from typing import Dict, Any

def validate_text_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate text input for sentiment analysis"""
    if not data:
        return {'valid': False, 'message': 'No data provided'}
    
    text = data.get('text', '')
    
    if not text:
        return {'valid': False, 'message': 'No text provided'}
    
    if not isinstance(text, str):
        return {'valid': False, 'message': 'Text must be a string'}
    
    text = text.strip()
    
    if not text:
        return {'valid': False, 'message': 'Text cannot be empty'}
    
    if len(text) > 5000:  # Reasonable limit
        return {'valid': False, 'message': 'Text too long (max 5000 characters)'}
    
    return {'valid': True, 'message': 'Valid input'}

def validate_pagination_params(page: int, per_page: int) -> Dict[str, Any]:
    """Validate pagination parameters"""
    if page < 1:
        return {'valid': False, 'message': 'Page must be >= 1'}
    
    if per_page < 1 or per_page > 100:
        return {'valid': False, 'message': 'Per page must be between 1 and 100'}
    
    return {'valid': True, 'message': 'Valid pagination'}

def validate_date_range(days: int) -> Dict[str, Any]:
    """Validate date range parameter"""
    if days < 1 or days > 365:
        return {'valid': False, 'message': 'Days must be between 1 and 365'}
    
    return {'valid': True, 'message': 'Valid date range'}