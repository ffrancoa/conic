use polars::prelude::*;
use crate::kernel::CoreError;
use crate::kernel::config::COL_DEPTH;


pub(crate) fn remove_rows(
    data: DataFrame,
    indicators: &[f64],
) -> Result<DataFrame, CoreError> {
    let indicators = Series::from_vec(
        "indicators".into(),
        indicators.to_vec(),
    );
    let indicators = lit(indicators).implode();

    let mask_expr: Vec<Expr> = data
        .get_column_names_str()
        .into_iter()
        .map(|name| col(name).is_in(indicators.clone(), false).not())
        .collect();
    let mask_expr = all_horizontal(mask_expr)?;

    let out_data = data
        .lazy()
        .filter(mask_expr)
        .collect()?;

    Ok(out_data)
}

pub(crate) fn replace_rows(
    data: DataFrame,
    indicators: &[f64],
    replace_value: &f64,
) -> Result<DataFrame, CoreError> {
    let indicators = Series::from_vec(
        "indicators".into(),
        indicators.to_vec(),
    );
    let indicators = lit(indicators).implode();

    let mask_expr: Vec<Expr> = data
        .get_column_names_str()
        .into_iter()
        .map(|name| col(name).is_in(indicators.clone(), false))
        .collect();
    let mask_expr = any_horizontal(mask_expr)?;

    let transform_expr: Vec<Expr> = data
        .get_column_names_str()
        .into_iter()
        .map(|name| {
            if name == *COL_DEPTH {
                col(name)
            } else {
                when(mask_expr.clone())
                    .then(lit(*replace_value))
                    .otherwise(col(name))
                    .alias(name)
            }
        })
        .collect();

    let out_data = data
        .lazy()
        .select(transform_expr)
        .collect()?;

    Ok(out_data)
}
