use polars::prelude::*;

use crate::CoreError;

/// Reads a CSV file into a `DataFrame`, inferring the schema.
pub fn read_csv(file_path: &str) -> Result<DataFrame, CoreError> {
    let mut lazy_frame = LazyCsvReader::new(PlPath::new(file_path))
        .with_infer_schema_length(Some(0))
        .finish()?;
    
    let schema = lazy_frame.collect_schema()?;

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