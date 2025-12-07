use polars::prelude::*;

use crate::CoreError;

/// Required columns for downstream calculations.
const REQUIRED_COLUMNS: [&str; 4] = ["Depth (m)", "qc (MPa)", "fs (kPa)", "u2 (kPa)"];

/// Reads a CSV file into a `DataFrame`, inferring the schema.
pub fn read_csv(file_path: &str) -> Result<DataFrame, CoreError> {
    let mut lazy_frame = LazyCsvReader::new(PlPath::new(file_path))
        .with_infer_schema_length(Some(0))
        .finish()?;
    
    let schema = lazy_frame.collect_schema()?;
    
    validate_columns(&schema)?;

    let raw_df = lazy_frame
        .select(
            schema.iter_names()
                .map(|name| {
                    let sname = name.as_str();
                    col(sname)
                        .cast(DataType::Float64)
                        .alias(sname)
                })
                .collect::<Vec<_>>(),
        )
        .collect()?;

    Ok(raw_df)
}

/// Validates that all required columns are present in the schema.
fn validate_columns(schema: &Arc<Schema>) -> Result<(), CoreError> {
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