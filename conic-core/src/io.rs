use polars::prelude::*;

use crate::CoreError;

/// Required columns for downstream calculations.
const REQUIRED_COLUMNS: [&str; 4] = ["Depth (m)", "qc (MPa)", "fs (kPa)", "u2 (kPa)"];

/// Reads a CSV file into a `DataFrame`, inferring the schema.
pub fn read_csv(file_path: &str) -> Result<DataFrame, CoreError> {
    let data = CsvReadOptions::default()
        .with_has_header(true)
        .with_infer_schema_length(None)
        .try_into_reader_with_file_path(Some(file_path.into()))?
        .finish()?;

    validate_columns(&data)?;

    let schema = data.schema().clone();

    let raw_data = data
        .lazy()
        .with_columns(
            schema
                .iter_names()
                .map(|name| col(name.as_str()).cast(DataType::Float64))
                .collect::<Vec<_>>(),
        )
        .collect()?;

    Ok(raw_data)
}

/// Validates that all required columns are present in the DataFrame.
fn validate_columns(data: &DataFrame) -> Result<(), CoreError> {
    let schema = data.schema();

    if let Some(missing) = REQUIRED_COLUMNS
        .iter()
        .find(|col| !schema.contains(col.as_ref()))
    {
        return Err(CoreError::InvalidData(format!(
            "Missing required column: {missing}"
        )));
    }
    Ok(())
}