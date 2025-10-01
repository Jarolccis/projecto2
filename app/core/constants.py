"""Security constants and messages."""

import os

# Keycloak configuration
PUBLIC_KEY_KEYCLOAK = os.getenv('KEYCLOAK_PUB', '')
public_key = f'-----BEGIN PUBLIC KEY-----\n{PUBLIC_KEY_KEYCLOAK}\n-----END PUBLIC KEY-----'
AUDIENCE = 'rebate-management-client'

# Error messages
TOKEN_NOT_VALID = 'Token no válido.'
TOKEN_REQUIRED = 'Token requerido.'
TOKEN_EXPIRED = 'Token expirado.'

USER_INACTIVE = 'El usuario se encuentra deshabilitado del sistema Rebates Management.'
NOT_BU = 'El usuario no tiene acceso a la unidad de negocio.'
NOT_ALLOW = 'No posee los permisos necesarios para continuar o ejecutar esta acción.'

# Lookup category codes
LOOKUP_CATEGORY_CODES = {
    'REBATE_TYPE': 'REBATE_TYPE',
    'CONCEPT': 'CONCEPT',
    'BILLING_TYPE': 'BILLING_TYPE',
    'PMM_USER_NAME': 'PMM_USER_NAME',
    'AGREEMENT_STATUSES': 'AGREEMENT_STATUSES',
    'STORE_GROUPING': 'STORE_GROUPING',
    'EXCLUDED_FLAGS': 'EXCLUDED_FLAGS',
    'AGREEMENT_BULK_UPLOAD_STATUSES': 'AGREEMENT_BULK_UPLOAD_STATUSES',
    'SOURCE_SYSTEM': 'SOURCE_SYSTEM'
}

# Individual lookup category constants
REBATE_TYPE_CATEGORY = 'REBATE_TYPE'
CONCEPT_CATEGORY = 'CONCEPT'
BILLING_TYPE_CATEGORY = 'BILLING_TYPE'
PMM_USER_NAME_CATEGORY = 'PMM_USER_NAME'
AGREEMENT_STATUSES_CATEGORY = 'AGREEMENT_STATUSES'
STORE_GROUPING_CATEGORY = 'STORE_GROUPING'
EXCLUDED_FLAGS_CATEGORY = 'EXCLUDED_FLAGS'
AGREEMENT_BULK_UPLOAD_STATUSES_CATEGORY = 'AGREEMENT_BULK_UPLOAD_STATUSES'
SOURCE_SYSTEM_CATEGORY = 'SOURCE_SYSTEM'

# Bulk upload templates paths
BULK_UPLOAD_TEMPLATES = {
    'SPF': 'templates/bulk-upload/plantilla_spf_v1.xlsx',
    'PMM': 'templates/bulk-upload/plantilla_pmm_v1.xlsx'
}
