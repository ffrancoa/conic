use polars::prelude::*;
use crate::CoreError;

/// Drop rows containing NaN value indicators
pub fn clean_nan_values(
    raw_df: DataFrame, nan_indicators: Vec<f64>
) -> Result<DataFrame, CoreError> {
    // create list series for is_in() (polars ≥0.50 requirement)
    let nan_series = Series::new(PlSmallStr::from("na_values"), nan_indicators)
        .implode()
        .map_err(CoreError::Polars)?
        .into_series();

    let mut exprs = Vec::new();
    for name in raw_df.get_column_names_str() {
        exprs.push(
            when(col(name).is_in(lit(nan_series.clone()), false))
                .then(lit(f64::NAN))
                .otherwise(col(name))
                .alias(name),
        );
    }

    let cleaned_df = raw_df
        .lazy()
        .select(exprs)
        .filter(all_horizontal([col("*").is_not_nan()])?)
        .collect()?;

    Ok(cleaned_df)
}

/// Drop rows containing any of the given value indicators
pub fn drop_value_rows(
    raw_df: DataFrame,
    value_indicators: Vec<f64>,
) -> Result<DataFrame, CoreError> {
    // create list series for is_in() (polars ≥0.50 requirement)
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
