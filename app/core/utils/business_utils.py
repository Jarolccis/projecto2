"""Business utility functions for domain layer."""

from typing import Optional


def get_bu_id(country: str) -> Optional[int]:
    """
    Get business unit ID based on country code.
    
    Args:
        country: Country ISO code (e.g., 'CL', 'PE')
        
    Returns:
        Business unit ID or None if country not supported
    """
    bu_mapping = {
        'CL': 4,
        'PE': 5
    }
    return bu_mapping.get(country)
