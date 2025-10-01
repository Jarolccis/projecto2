"""Unified validator combining all validation functionalities."""

import re
import time
import unicodedata
from typing import List, Optional, Any
from dataclasses import dataclass

import bleach


@dataclass
class ValidationResult:
    """Result of validation with detailed information."""
    is_valid: bool
    sanitized_value: Any
    errors: list
    warnings: list
    validation_time: float


class UnifiedValidator:
    """Unified validator that combines all validation approaches."""
    
    def __init__(self):
        # SQL Injection patterns (from security_validator_schema.py)
        self.sql_patterns = [
            r'(?i)(select|insert|update|delete|drop|create|alter)',
            r'(?i)(exec|execute|script|javascript|vbscript)',
            r'(?i)(onload|onerror|onclick|onmouseover)',
            r'(\-\-|\/\*|\*\/|\;|\|\||&&)',
            r'(\b(0x[0-9a-fA-F]+)\b)',  # Hexadecimal values
            r'(\b(0b[01]+)\b)',          # Binary values
            r'(?i)(\bor\b|\band\b)',     # OR/AND operators
        ]
        
        # NoSQL Injection patterns
        self.nosql_patterns = [
            r'(\$where|\$ne|\$gt|\$lt|\$gte|\$lte)',
            r'(\$regex|\$options|\$text|\$search)',
            r'(\$or|\$and|\$not|\$nor)',
            r'(\$exists|\$type|\$mod|\$in|\$nin)',
            r'(\$all|\$elemMatch|\$size|\$push|\$pull)',
            r'(\$inc|\$set|\$unset|\$rename|\$currentDate)',
        ]
        
        # Suspicious patterns
        self.suspicious_patterns = [
            r'\.\.',           # Directory traversal
            r'\/\/',           # URL injection
            r'\\\\',           # Path injection
            r'\.\.\/',         # Directory traversal
            r'\.\.\\',         # Windows path injection
        ]
    
    def validate_input_layer(self, data: str, field_name: str) -> ValidationResult:
        """Basic input validation layer."""
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            if not data or not str(data).strip():
                errors.append(f"{field_name} cannot be empty")
                return ValidationResult(False, None, errors, warnings, time.time() - start_time)
            
            # Basic length validation
            if len(str(data)) > 1000:  # Absolute maximum
                errors.append(f"{field_name} too long (max 1000 characters)")
            
            return ValidationResult(True, data, errors, warnings, time.time() - start_time)
            
        except Exception as e:
            errors.append(f"Basic validation failed: {str(e)}")
            return ValidationResult(False, None, errors, warnings, time.time() - start_time)
    
    def validate_security_layer(self, data: str, field_name: str) -> ValidationResult:
        """Security validation layer."""
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            sanitized = str(data).strip()
            
            # Check SQL Injection patterns
            for pattern in self.sql_patterns:
                if re.search(pattern, sanitized):
                    errors.append(f"{field_name} contains SQL injection patterns")
                    break
            
            # Check NoSQL Injection patterns
            for pattern in self.nosql_patterns:
                if re.search(pattern, sanitized, re.IGNORECASE):
                    errors.append(f"{field_name} contains NoSQL injection patterns")
                    break
            
            # Check suspicious patterns
            for pattern in self.suspicious_patterns:
                if re.search(pattern, sanitized):
                    errors.append(f"{field_name} contains suspicious patterns")
                    break
            
            # Check for control characters and null bytes
            control_errors = self._check_control_characters(sanitized, field_name)
            errors.extend(control_errors)
            
            if errors:
                return ValidationResult(False, None, errors, warnings, time.time() - start_time)
            
            return ValidationResult(True, sanitized, errors, warnings, time.time() - start_time)
            
        except Exception as e:
            errors.append(f"Security validation failed: {str(e)}")
            return ValidationResult(False, None, errors, warnings, time.time() - start_time)
    
    def validate_business_layer(self, data: str, field_name: str, 
                               min_length: int = 3, max_length: int = 100,
                               allowed_chars: Optional[str] = None) -> ValidationResult:
        """Business logic validation layer."""
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            sanitized = str(data).strip()
            
            # Length validation
            if len(sanitized) < min_length:
                errors.append(f"{field_name} too short (min {min_length} characters)")
            
            if len(sanitized) > max_length:
                errors.append(f"{field_name} too long (max {max_length} characters)")
            
            # Character validation
            if allowed_chars and not re.match(allowed_chars, sanitized):
                errors.append(f"{field_name} contains unsupported characters")
            
            # Generic name validation
            generic_names = ['test', 'admin', 'root', 'user', 'demo', 'example', 'sample']
            if sanitized.lower() in generic_names:
                warnings.append(f"{field_name} is generic")
            
            # Repeated characters validation
            if re.search(r'(.)\1{4,}', sanitized):
                warnings.append(f"{field_name} contains many repeated characters")
            
            if errors:
                return ValidationResult(False, None, errors, warnings, time.time() - start_time)
            
            return ValidationResult(True, sanitized, errors, warnings, time.time() - start_time)
            
        except Exception as e:
            errors.append(f"Business validation failed: {str(e)}")
            return ValidationResult(False, None, errors, warnings, time.time() - start_time)
    
    def validate_integrity_layer(self, data: str, field_name: str) -> ValidationResult:
        """Data integrity validation layer."""
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            sanitized = str(data).strip()
            
            # HTML sanitization
            sanitized = self._sanitize_html(sanitized)
            
            # Unicode normalization
            normalized = self._normalize_unicode(sanitized)
            
            # Extra whitespace normalization
            final_value = re.sub(r'\s+', ' ', normalized).strip()
            
            return ValidationResult(True, final_value, errors, warnings, time.time() - start_time)
            
        except Exception as e:
            errors.append(f"Integrity validation failed: {str(e)}")
            return ValidationResult(False, None, errors, warnings, time.time() - start_time)
    
    def validate_with_timing_protection(self, data: str, field_name: str,
                                      min_length: int = 3, max_length: int = 100,
                                      allowed_chars: Optional[str] = None,
                                      generic_names: Optional[List[str]] = None) -> ValidationResult:
        """Complete validation with timing protection."""
        start_time = time.time()
        
        try:
            # Layer 1: Basic input validation
            result = self.validate_input_layer(data, field_name)
            if not result.is_valid:
                return result
            
            # Layer 2: Security validation
            result = self.validate_security_layer(data, field_name)
            if not result.is_valid:
                return result
            
            # Layer 3: Business logic validation
            result = self.validate_business_layer(data, field_name, min_length, max_length, allowed_chars)
            if not result.is_valid:
                return result
            
            # Layer 4: Data integrity validation
            result = self.validate_integrity_layer(data, field_name)
            if not result.is_valid:
                return result
            
            # Timing attack protection
            self._timing_attack_protection(start_time)
            
            return result
            
        except Exception as e:
            # Normalize error response time
            self._timing_attack_protection(start_time)
            
            return ValidationResult(False, None, [f"Validation failed: {str(e)}"], [], time.time() - start_time)
    
    def validate_simple(self, value: str, allowed_pattern: str, field_name: str,
                       max_repeated_chars: int = 3, normalize_whitespace: bool = True,
                       to_upper: bool = False) -> str:
        """Simple validation for backward compatibility with original validators.py."""
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")
        
        # Normalize whitespace if requested
        if normalize_whitespace:
            value = re.sub(r'\s+', ' ', value.strip())
        
        # Convert to uppercase if requested
        if to_upper:
            value = value.upper()
        
        # Check for repeated characters
        if max_repeated_chars > 0:
            for i in range(len(value) - max_repeated_chars + 1):
                if len(set(value[i:i + max_repeated_chars + 1])) == 1:
                    raise ValueError(f"{field_name} cannot have more than {max_repeated_chars} repeated characters")
        
        # Check against allowed pattern
        if not re.match(allowed_pattern, value):
            raise ValueError(f"{field_name} contains invalid characters")
        
        return value
    
    def validate_secure_string(self, value: str, allowed_pattern: str, field_name: str = "Value",
                              min_length: int = 1, max_length: int = 255, max_repeated_chars: int = 10,
                              normalize_whitespace: bool = True, to_upper: bool = False,
                              required: bool = True, forbidden_generic_names: Optional[List[str]] = None) -> str:
        """Complete secure string validation with timing attack protection."""
        start_time = time.time()
        
        try:
            if not required and (not value or not value.strip()):
                return value if value is not None else ""
            
            if not value or not value.strip():
                raise ValueError(f"{field_name} cannot be empty or only whitespace")
            
            # Normalize whitespace
            if normalize_whitespace:
                if to_upper:
                    sanitized = re.sub(r'\s+', '_', value.strip().upper())
                else:
                    sanitized = re.sub(r'\s+', ' ', value.strip())
            else:
                sanitized = value.strip()
                if to_upper:
                    sanitized = sanitized.upper()
            
            # Length validation
            if len(sanitized) < min_length:
                raise ValueError(f"{field_name} too short (min {min_length} characters)")
            
            if len(sanitized) > max_length:
                raise ValueError(f"{field_name} too long (max {max_length} characters)")
            
            # Generic names validation
            if forbidden_generic_names and sanitized.lower() in [name.lower() for name in forbidden_generic_names]:
                raise ValueError(f"{field_name} is too generic")
            
            # Security validations
            self._validate_sql_injection(sanitized)
            self._validate_nosql_injection(sanitized)
            self._validate_suspicious_patterns(sanitized)
            self._validate_repeated_characters(sanitized, max_repeated_chars)
            
            # Format validation
            if not re.match(allowed_pattern, sanitized):
                raise ValueError(f"{field_name} contains invalid characters")
            
            # HTML sanitization
            sanitized = self._sanitize_html(sanitized)
            
            # Unicode normalization
            normalized = self._normalize_unicode(sanitized)
            
            # Control character validation
            self._validate_control_characters(normalized)
            
            # Timing attack protection
            self._timing_attack_protection(start_time)
            
            return normalized
            
        except Exception as e:
            # Normalize error timing
            self._timing_attack_protection(start_time)
            raise e
    
    def _validate_sql_injection(self, value: str) -> None:
        """Validate against SQL injection patterns."""
        for pattern in self.sql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Value contains potentially malicious SQL patterns")
    
    def _validate_nosql_injection(self, value: str) -> None:
        """Validate against NoSQL injection patterns."""
        for pattern in self.nosql_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Value contains NoSQL injection patterns")
    
    def _validate_suspicious_patterns(self, value: str) -> None:
        """Validate against suspicious patterns."""
        for pattern in self.suspicious_patterns:
            if re.search(pattern, value):
                raise ValueError("Value contains suspicious patterns")
    
    def _validate_repeated_characters(self, value: str, max_repetition: int = 10) -> None:
        """Validate against excessive character repetition."""
        pattern = rf'(.)\1{{{max_repetition},}}'
        if re.search(pattern, value):
            raise ValueError(f"Value contains too many repeated characters (max {max_repetition})")
    
    def _check_control_characters(self, value: str, field_name: str) -> List[str]:
        """Check for control characters and null bytes, return list of errors."""
        errors = []
        
        if '\x00' in value:
            errors.append(f"{field_name} contains null bytes")
        
        if re.search(r'[\x00-\x1f\x7f-\x9f]', value):
            errors.append(f"{field_name} contains control characters")
        
        return errors
    
    def _validate_control_characters(self, value: str) -> None:
        """Validate against null bytes and control characters."""
        errors = self._check_control_characters(value, "Value")
        if errors:
            raise ValueError(errors[0])  # Raise first error
    
    def _sanitize_html(self, value: str) -> str:
        """Sanitize HTML content."""
        return bleach.clean(
            value,
            tags=[],
            attributes={},
            protocols=[],
            strip=True,
            strip_comments=True
        )
    
    def _normalize_unicode(self, value: str) -> str:
        """Normalize Unicode to prevent encoding attacks."""
        return unicodedata.normalize('NFKC', value)
    
    def _timing_attack_protection(self, start_time: float, min_duration: float = 0.1) -> None:
        """Protect against timing attacks by normalizing execution time."""
        elapsed = time.time() - start_time
        if elapsed < min_duration:
            time.sleep(min_duration - elapsed)


# Global validator instance
unified_validator = UnifiedValidator()


# Backward compatibility functions
def validate_secure_string(value: str, allowed_pattern: str, field_name: str,
                          max_repeated_chars: int = 3, normalize_whitespace: bool = True,
                          to_upper: bool = False) -> str:
    """
    Backward compatibility function for simple validation.
    
    Args:
        value: The string value to validate
        allowed_pattern: Regex pattern for allowed characters
        field_name: Name of the field for error messages
        max_repeated_chars: Maximum number of repeated characters allowed
        normalize_whitespace: Whether to normalize whitespace
        to_upper: Whether to convert to uppercase
        
    Returns:
        Validated and sanitized string
        
    Raises:
        ValueError: If validation fails
    """
    return unified_validator.validate_simple(
        value=value,
        allowed_pattern=allowed_pattern,
        field_name=field_name,
        max_repeated_chars=max_repeated_chars,
        normalize_whitespace=normalize_whitespace,
        to_upper=to_upper
    )


def validate_secure_string_advanced(value: str, allowed_pattern: str, field_name: str = "Value",
                                   min_length: int = 1, max_length: int = 255, 
                                   max_repeated_chars: int = 10, normalize_whitespace: bool = True,
                                   to_upper: bool = False, required: bool = True,
                                   forbidden_generic_names: Optional[List[str]] = None) -> str:
    """
    Advanced secure string validation with timing attack protection.
    
    Args:
        value: String to validate
        allowed_pattern: Regex pattern for allowed characters
        field_name: Name of the field for error messages
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        max_repeated_chars: Maximum allowed repeated characters
        normalize_whitespace: Whether to normalize whitespace
        to_upper: Whether to convert to uppercase
        required: Whether the field is required
        forbidden_generic_names: List of generic names to reject
        
    Returns:
        Validated and sanitized string
        
    Raises:
        ValueError: If validation fails
    """
    return unified_validator.validate_secure_string(
        value=value,
        allowed_pattern=allowed_pattern,
        field_name=field_name,
        min_length=min_length,
        max_length=max_length,
        max_repeated_chars=max_repeated_chars,
        normalize_whitespace=normalize_whitespace,
        to_upper=to_upper,
        required=required,
        forbidden_generic_names=forbidden_generic_names
    )


def validate_with_timing_protection(value: str, field_name: str,
                                  min_length: int = 3, max_length: int = 100,
                                  allowed_chars: Optional[str] = None,
                                  generic_names: Optional[List[str]] = None) -> str:
    """
    Validation with timing protection, returns string.
    
    Args:
        value: String to validate
        field_name: Name of the field for error messages
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        allowed_chars: Regex pattern for allowed characters
        generic_names: List of generic names to reject
        
    Returns:
        Validated and sanitized string
        
    Raises:
        ValueError: If validation fails
    """
    result = unified_validator.validate_with_timing_protection(
        data=value,
        field_name=field_name,
        min_length=min_length,
        max_length=max_length,
        allowed_chars=allowed_chars,
        generic_names=generic_names
    )
    
    if not result.is_valid:
        raise ValueError(f"Validation failed: {', '.join(result.errors)}")
    
    return result.sanitized_value


# Export the main validator class for advanced usage
__all__ = [
    'UnifiedValidator',
    'ValidationResult',
    'unified_validator',
    'validate_secure_string',
    'validate_secure_string_advanced',
    'validate_with_timing_protection'
]
