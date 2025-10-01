from typing import List, Optional, Union


def format_array(arr: Optional[List[str]] = None) -> Optional[List[str]]:
    if not arr:
        return None
    return arr


def format_text_array(arr: Optional[List[str]] = None) -> Optional[str]:
    if not arr:
        return None
    return ','.join(f"'{item}'" for item in arr)


def format_text_array_with_wildcard(arr: Optional[List[str]] = None) -> Optional[str]:
    """Format a list of strings into IN clause with % wildcard at the end."""
    if not arr:
        return None
    return ','.join(f"'{item}%'" for item in arr)


def format_like_pattern(arr: Optional[List[str]] = None) -> Optional[str]:
    """Format a list of strings into a single LIKE pattern for SQL."""
    if not arr:
        return None
    
    # Tomamos el primer patrón y le agregamos % si no lo tiene
    pattern = arr[0].strip()
    
    # Si el patrón no termina con %, lo agregamos para búsqueda parcial
    if not pattern.endswith('%'):
        pattern = f"{pattern}%"
    
    return pattern


def format_numeric_array(arr: Optional[List[Union[int, float]]] = None) -> Optional[List[Union[int, float]]]:
    if not arr:
        return None
    return arr
