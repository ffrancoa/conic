use polars::prelude::*;
use crate::kernel::{CoreError, ConicDataFrame};
use crate::kernel::config::{COL_DEPTH, COL_QC, COL_FS, COL_U2, COL_U0};

/// Reads a CSV file into a `ConicDataFrame` with predefined schema.
///
/// All columns are read as `Float64`.
pub fn read_csv(file_path: &str) -> Result<ConicDataFrame, CoreError> {
    let required_columns = [*COL_DEPTH, *COL_QC, *COL_FS, *COL_U2, *COL_U0];

    let schema = Schema::from_iter(
        required_columns
            .iter()
            .map(|&name| Field::new(name.into(), DataType::Float64))
    );

    let raw_data = CsvReadOptions::default()
        .with_has_header(true)
        .with_schema(Some(Arc::new(schema)))
        .try_into_reader_with_file_path(Some(file_path.into()))?
        .finish()
        .map_err(|_err| {
            CoreError::InvalidData(format!(
                "Failed to read CSV file. Ensure all required columns \
                 are present: {:?}.",
                required_columns,
            ))
        })?;

    Ok(ConicDataFrame::new(raw_data))
}