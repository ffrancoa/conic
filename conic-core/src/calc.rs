use polars::prelude::*;
use crate::CoreError;

/// Filter out rows containing any of the given value indicators
pub fn filter_value_rows(
    raw_df: DataFrame,
    value_indicators: Vec<f64>,
) -> Result<DataFrame, CoreError> {
    // create list series for is_in() (polars ≥ 0.50 requirement)
    let val_series = Series::new(PlSmallStr::from("indicators"), value_indicators)
        .implode()
        .map_err(CoreError::Polars)?
        .into_series();

    let conditions: Vec<Expr> = raw_df
        .get_column_names_str()
        .into_iter()
        .map(|name| col(name).is_in(lit(val_series.clone()), false).not())
        .collect();

    let filtered_df = raw_df
        .lazy()
        .filter(all_horizontal(conditions)?)
        .collect()?;

    Ok(filtered_df)
}
