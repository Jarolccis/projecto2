SELECT DISTINCT
sku.COD_SKU                         as Sku,
sku.DESC_SKU                        as DescripcionSku,  
sku.F_COSTO_RPSC                    as CostoReposicion,
sku.ID_ESTADO                       as EstadoId, 
sku.ID_MARCA                        as MarcaId,
mar.DESC_MARCA                      as Marca,
sku.ID_SUBCLASE                     as SubClaseId,
scls.COD_SUBCLASE                   as CodigoSubClase,
scls.DESC_SUBCLASE                  as SubClase,
sku.ID_CLASE                        as ClaseId,
cls.COD_CLASE                       as CodigoClase,
cls.DESC_CLASE                      as Clase,
sku.ID_SUPDEPARTAMENTO              as SubDepartamentoId,
sdpto.COD_SUBDEPARTAMENTO           as CodigoSubDepartamento,
sdpto.DESC_SUBDEPARTAMENTO          as SubDepartamento,
sku.ID_DEPARTAMENTO                 as DepartamentoId,
dpto.COD_DEPARTAMENTO               as CodigoDepartamento,
dpto.DESC_DEPARTAMENTO              as Departamento,
sku.ID_DIVISION                     as DivisionId,
div.COD_DIVISION                    as CodigoDivision,
div.DESC_DIVISION                   as Division,
sku.ID_PROVEEDOR_DEF                as ProveedorId,
IFNULL(prv.RUT_RUC, '')             as RucProveedor,
IFNULL(prv.DESC_PROVEEDOR, '')      as Proveedor
FROM `tot-bi-corp-datalake-prd.acc_tot_bi_pe_prd.LK_PRO_SKU` sku    
LEFT JOIN `tot-bi-corp-datalake-prd.acc_tot_bi_pe_prd.LK_PRO_DIVISION` div on div.ID_DIVISION = sku.ID_DIVISION  
LEFT JOIN `tot-bi-corp-datalake-prd.acc_tot_bi_pe_prd.LK_PRO_DEPARTAMENTO` dpto on dpto.ID_DEPARTAMENTO = sku.ID_DEPARTAMENTO 
LEFT JOIN `tot-bi-corp-datalake-prd.acc_tot_bi_pe_prd.LK_PRO_SUBDEPARTAMENTO` sdpto on sdpto.ID_SUPDEPARTAMENTO = sku.ID_SUPDEPARTAMENTO  
LEFT JOIN `tot-bi-corp-datalake-prd.acc_tot_bi_pe_prd.LK_PRO_CLASE` cls on cls.ID_ClASE = sku.ID_CLASE 
LEFT JOIN `tot-bi-corp-datalake-prd.acc_tot_bi_pe_prd.LK_PRO_SUBCLASE` scls on scls.ID_SUBCLASE = sku.ID_SUBCLASE  
LEFT JOIN `tot-bi-corp-datalake-prd.acc_tot_bi_pe_prd.LK_PRO_MARCA` mar on mar.ID_MARCA = sku.ID_MARCA 
LEFT JOIN `tot-bi-corp-datalake-prd.acc_tot_bi_pe_prd.LK_PRV_PROVEEDOR` prv ON prv.ID_PROVEEDOR = sku.ID_PROVEEDOR_DEF    
WHERE sku.COD_SKU LIKE ANY({sku_codes})
LIMIT 20