from pathlib import Path

import polars as pl


def read_csv(
    path: Path | str, *, delimiter: str = ",", skip_records: int = 0
) -> pl.DataFrame:
    """Read a CPTu CSV file and cast all columns to Float64.

    Columns are read as strings and then cast, since Polars
    cannot assign a target dtype to columns whose names are
    not known in advance. The cast is strict: any residual
    non-numeric value (e.g. a leftover units row) raises,
    which surfaces a misplaced ``skip_records`` instead of
    passing silently.

    Parameters
    ----------
    path : Path or str
        Path to the CSV file containing the CPTu data.
    delimiter : str, default ","
        Column separator character.
    skip_records : int, default 0
        Number of data rows to skip *after* the header
        (e.g. to bypass units rows such as 'm', 'MPa',
        'kPa'). Set this to isolate the numeric matrix.

    Returns
    -------
    pl.DataFrame
        DataFrame with every column typed as
        ``pl.Float64``.

    Raises
    ------
    polars.exceptions.InvalidOperationError
        If any column holds non-numeric values after
        ``skip_records`` is applied.

    Examples
    --------
    >>> data = read_csv(
    ...     "project_alpha/cpt01.csv",
    ...     delimiter=";",
    ...     skip_records=1,
    ... )
    >>> data.schema
    Schema({
        'depth': Float64,
        'qc': Float64,
        'fs': Float64,
        'u2': Float64,
    })
    """
    return pl.read_csv(
        path,
        has_header=True,
        infer_schema=False,
        raise_if_empty=True,
        separator=delimiter,
        skip_rows_after_header=skip_records,
    ).cast({pl.String: pl.Float64})


def read_excel(
    path: Path | str,
    *,
    sheet_number: int | None = None,
    sheet_name: str | None = None,
    header_row: int = 1,
) -> pl.DataFrame:
    """Read a CPTu Excel workbook with full schema inference.

    Column types are inferred from the workbook itself, which
    scans every row to resolve types reliably. If neither
    ``sheet_number`` nor ``sheet_name`` is given, the first
    sheet is read.

    Parameters
    ----------
    path : Path or str
        Path to the Excel file (.xlsx, .xls) containing
        the CPTu data.
    sheet_number : int or None, optional
        1-based index of the sheet to read. If both
        ``sheet_number`` and ``sheet_name`` are given,
        ``sheet_name`` takes precedence.
    sheet_name : str or None, optional
        Name of the sheet to read.
    header_row : int, default 1
        1-based position of the header row, used to skip
        any preceding banner or metadata rows above the
        column names.

    Returns
    -------
    pl.DataFrame
        DataFrame with column types inferred from the
        workbook.

    Raises
    ------
    polars.exceptions.NoDataError
        If the selected sheet is empty.

    Examples
    --------
    >>> data = read_excel(
    ...     "project_betta/cpt02.xlsx",
    ...     sheet_name="CPTu_02",
    ...     header_row=2,
    ... )
    """
    return pl.read_excel(
        path,
        has_header=True,
        infer_schema_length=None,
        sheet_id=sheet_number,
        sheet_name=sheet_name,
        raise_if_empty=True,
        read_options={"header_row": header_row - 1},
    )
