from io import BytesIO
import pandas as pd

def get_azure_container_name(country: str) -> str or None:
    """
    Return the Azure container name if country is valid.
    :param country: Country ISO code
    :return: str or None
    """
    container_mapping = {
        'CL': 'rbm-tot-cl',
        'PE': 'rbm-tot-pe'
    }
    return container_mapping.get(country)

def dataframe_to_excel(
        df: pd.DataFrame,
        sheet_name: str = 'Hoja1',
        columns: list[str] = None,
        columns_to_percent_format: list[str] = None,
        columns_to_number_format: list[str] = None,
        return_as_bytes: bool = True,
        date_format: str = 'dd-mm-yyyy',
        percent_format: str = '0.00%',
        number_format: str = '#,##0'
) -> BytesIO or bytes:
    buffer = BytesIO()
    writer = pd.ExcelWriter(buffer, date_format=date_format, engine='xlsxwriter')
    if not columns:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    else:
        df[columns].to_excel(writer, index=False, sheet_name=sheet_name)

    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    for idx, col in enumerate(df):
        if col in columns_to_percent_format:
            n_format = workbook.add_format({'num_format': percent_format})
            worksheet.set_column(idx, idx, 20, n_format)
        elif col in columns_to_number_format:
            p_format = workbook.add_format({'num_format': number_format})
            worksheet.set_column(idx, idx, 20, p_format)
        else:
            worksheet.set_column(idx, idx, 20)

    # Add auto filter.
    worksheet.autofilter(0, 0, df.shape[0], df.shape[1] - 1)

    writer.close()
    buffer.seek(0)
    if return_as_bytes:
        return buffer.getvalue()
    return buffer