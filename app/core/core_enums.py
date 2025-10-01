"""Core domain enums."""

from enum import Enum


class CurrencyEnum(Enum):
    """Currency enumeration.
    
    Currency codes with their corresponding database IDs.
    Format: CODE = ID (integer)
    """
    
    USD = 2  # Dólar
    PEN = 3  # Sol Peruano
    
    @classmethod
    def get_currency_name(cls, code) -> str:
        """Get the full currency name by code."""
        currency_names = {
            cls.USD: "Dólar",
            cls.PEN: "Sol Peruano"
        }
        return currency_names.get(code, "Unknown Currency")
    
    @classmethod
    def get_currency_id(cls, code) -> int:
        """Get the database ID by currency code."""
        return code.value
    
    @classmethod
    def get_by_id(cls, currency_id: int):
        """Get currency enum by database ID."""
        for currency in cls:
            if currency.value == currency_id:
                return currency
        return None
