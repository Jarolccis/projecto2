select
    DivisionId as division_id,
    Codigo as division_code,
    Descripcion as division_name
from
    `{project_id}.tot_pe_data_proveedor.division`
order by Codigo asc