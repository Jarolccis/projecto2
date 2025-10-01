
from app.domain.entities.lookup import LookupValueResult


def map_query_result_to_lookup_value_result(row) -> LookupValueResult:
    return LookupValueResult(
        lookup_value_id=row.lookup_value_id,
        option_key=row.option_key,
        display_value=row.display_value,
        option_value=row.option_value,
        metadata=row.metadata or {},
        sort_order=row.sort_order,
        parent_id=row.parent_id
    )
