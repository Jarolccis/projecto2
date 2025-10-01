"""Keycloak authentication strategy implementation."""

from typing import Optional

import jwt
from app.interfaces.schemas.security_schema import User, ResponseValidToken, TokenData
from app.domain.repositories.security_repository import AuthenticationStrategy
from app.core.constants import public_key, AUDIENCE
from app.core.utils import get_bu_id


class KeyCloakStrategy(AuthenticationStrategy):
    """Keycloak implementation of authentication strategy."""

    def valid_token(self, token: str) -> ResponseValidToken:
        """
        Check if the decoded jwt token is valid by "KEYCLOAK_PUB".
        """
        try:
            payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=AUDIENCE)
            
            return ResponseValidToken(
                is_valid=True,
                token_data=TokenData(**payload),
                reason_reject=''
            )
        except jwt.ExpiredSignatureError:
            return ResponseValidToken(
                is_valid=False,
                token_data=None,
                reason_reject='Tu sesión en Rebates Management ha expirado.'
            )
        except jwt.InvalidAudienceError:
            return ResponseValidToken(
                is_valid=False,
                token_data=None,
                reason_reject=f'Token audience inválido. Esperado: {AUDIENCE}'
            )
        except jwt.InvalidSignatureError:
            return ResponseValidToken(
                is_valid=False,
                token_data=None,
                reason_reject='Firma del token inválida.'
            )
        except jwt.DecodeError:
            return ResponseValidToken(
                is_valid=False,
                token_data=None,
                reason_reject='Error al decodificar el token.'
            )
        except jwt.InvalidTokenError:
            return ResponseValidToken(
                is_valid=False,
                token_data=None,
                reason_reject='Token no válido para Rebates Management.'
            )
        except Exception:
            return ResponseValidToken(
                is_valid=False,
                token_data=None,
                reason_reject='Error en control de jwt Rebates Management.'
            )

    def has_bu(self, bu: str, country: str, vendor_tax: Optional[str] = None, user: Optional[User] = None) -> bool:
        """
        Check if a business unit (bu) and a country exist in the vendors list,
        optionally filtering by vendor_tax.
        """
        if not user or not user.vendors_taxs:
            return False

        filtered_data = (
            [vendor for vendor in user.vendors_taxs if vendor.taxId == vendor_tax]
            if vendor_tax else user.vendors_taxs
        )

        for vendor in filtered_data:
            for op in vendor.operation:
                if op.businessUnit == bu and country in op.country:
                    bu_id = get_bu_id(country)
                    if bu_id:
                        return True
        return False

    def has_permissions(self, permissions: list[str], user: User) -> bool:
        """
        Verify user roles in Audience.
        """
        if not user.resource_access or AUDIENCE not in user.resource_access:
            return False
        
        user_roles = user.resource_access[AUDIENCE].get('roles', [])
        return all(permission in user_roles for permission in permissions)

    def get_user(self, response_valid_token: ResponseValidToken) -> User:
        """
        User extracted by token data.
        """
        if not response_valid_token.token_data:
            raise ValueError("Token data is required")
            
        user = User(**response_valid_token.token_data.model_dump(by_alias=True))
        return user

    def is_active(self) -> bool:
        """
        Verify active user, but the state is the responsibility of Keycloak.
        """
        return True
