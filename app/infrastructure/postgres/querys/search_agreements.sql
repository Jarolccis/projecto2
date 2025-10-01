-- Search agreements using PostgreSQL stored function
-- This query calls the fn_search_agreements function with all search parameters

SELECT * FROM tottus_pe.fn_search_agreements(
    p_division_codes => :division_codes,
    p_status_ids => :status_ids,
    p_created_by_emails => :created_by_emails,
    p_agreement_number => :agreement_number,
    p_sku_code => :sku_code,
    p_description => :description,
    p_rebate_type_id => :rebate_type_id,
    p_concept_id => :concept_id,
    p_spf_code => :spf_code,
    p_spf_description => :spf_description,
    p_start_date => :start_date,
    p_end_date => :end_date,
    p_supplier_ruc => :supplier_ruc,
    p_supplier_name => :supplier_name,
    p_store_grouping_id => :store_grouping_id,
    p_pmm_username => :pmm_username,
    p_limit => :limit,
    p_offset => :offset
);
