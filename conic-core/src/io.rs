use polars::prelude::*;

use crate::CoreError;


const COL_DEPTH: &str = "Depth (m)";
const COL_QC: &str = "qc (MPa)";
const COL_FS: &str = "fs (kPa)";
const COL_U2: &str = "u2 (kPa)";
const COL_U0: &str = "u0 (kPa)";

const REQUIRED_COLUMNS: [&str; 5] = [COL_DEPTH, COL_QC, COL_FS, COL_U2, COL_U0];


/// Reads a CSV file into a `DataFrame` with predefined schema.
///
/// All columns are read as `Float64`.
pub fn read_csv(file_path: &str) -> Result<DataFrame, CoreError> {
    let schema = Schema::from_iter(
        REQUIRED_COLUMNS
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
                REQUIRED_COLUMNS,
            ))
        })?;

    Ok(raw_data)
}