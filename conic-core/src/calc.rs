use polars::prelude::*;
use crate::CoreError;

/// Filter out rows containing any of the given value indicators
pub fn filter_rows(
    raw_df: DataFrame,
    filter_values: Vec<f64>,
) -> Result<DataFrame, CoreError> {
    // create list series for is_in() (polars ≥ 0.50 requirement)
    let filter_series = Series::new(PlSmallStr::from("indicators"), filter_values)
        .implode()?
        .into_series();

    let mask = all_horizontal(
        raw_df
            .get_column_names_str()
            .into_iter()
            .map(|name| col(name).is_in(lit(filter_series.clone()), false).not())
            .collect::<Vec<Expr>>(),
    )?;

    let filtered_df = raw_df
        .lazy()
        .filter(mask)
        .collect()?;

    Ok(filtered_df)
}
