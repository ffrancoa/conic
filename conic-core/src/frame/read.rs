use polars::prelude::*;
use crate::kernel::{CoreError, ConicDataFrame};
use crate::kernel::config::{
    COL_DEPTH, COL_QC, COL_FS, COL_U2, COL_U0, GAMMA_W, WATER_LEVEL
};

/// Reads a CSV file into a `ConicDataFrame` with predefined schema.
///
/// Required columns: Depth, qc, fs, u2
/// Optional columns: u0 (if missing, calculated from water_level)
///
/// All columns are read or cast to `Float64`.
pub fn read_csv(file_path: &str) -> Result<ConicDataFrame, CoreError> {
    let required_columns = [*COL_DEPTH, *COL_QC, *COL_FS, *COL_U2];

    // read CSV with schema overrides to ensure all numeric columns are Float64
    let schema_overrides = Schema::from_iter(vec![
        Field::new((*COL_DEPTH).into(), DataType::Float64),
        Field::new((*COL_QC).into(), DataType::Float64),
        Field::new((*COL_FS).into(), DataType::Float64),
        Field::new((*COL_U2).into(), DataType::Float64),
        Field::new((*COL_U0).into(), DataType::Float64),
    ]);

    let raw_data = CsvReadOptions::default()
        .with_has_header(true)
        .with_schema_overwrite(Some(Arc::new(schema_overrides)))
        .try_into_reader_with_file_path(Some(file_path.into()))?
        .finish()
        .map_err(|err| {
            CoreError::InvalidData(format!(
                "Failed to read CSV file '{}': {}",
                file_path, err
            ))
        })?;

    // validate required columns and check for u0
    let column_names = raw_data.get_column_names();

    // check all required columns are present
    if let Some(missing) = required_columns.iter()
        .find(|&&col| !column_names.iter().any(|name| name.as_str() == col)) {
        return Err(CoreError::InvalidData(format!(
            "Missing required column '{}'. Required columns: {:?}",
            missing, required_columns
        )));
    }

    let has_u0 = column_names.iter().any(|name| name.as_str() == *COL_U0);

    // cast required columns to Float64
    let mut cast_exprs: Vec<Expr> = required_columns
        .iter()
        .map(|&col_name| col(col_name).cast(DataType::Float64))
        .collect();

    // if u0 exists, cast it; otherwise calculate it
    if has_u0 {
        cast_exprs.push(col(*COL_U0).cast(DataType::Float64));
    } else {
        cast_exprs.push(
            when(col(*COL_DEPTH).gt_eq(lit(*WATER_LEVEL)))
                .then((col(*COL_DEPTH) - lit(*WATER_LEVEL)) * lit(*GAMMA_W))
                .otherwise(lit(0.0))
                .alias(*COL_U0)
        );
    }

    let raw_data = raw_data
        .lazy()
        .select(cast_exprs)
        .collect()
        .map_err(|err| {
            CoreError::InvalidData(format!(
                "Failed to process columns: {}",
                err
            ))
        })?;

    Ok(ConicDataFrame::new(raw_data))
}