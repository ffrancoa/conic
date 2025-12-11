use polars::prelude::*;
use polars::series::ops::NullBehavior;
use crate::kernel::CoreError;
use crate::kernel::config::COL_DEPTH;

pub(crate) fn adjust_depth(
    data: DataFrame,
    start_depth: Option<f64>,
    spacing: Option<f64>,
) -> Result<DataFrame, CoreError> {
    let n_rows = data.height();

    if n_rows == 0 {
        return Err(CoreError::InvalidData(
            "Cannot adjust depth: DataFrame is empty".to_string()
        ));
    }

    if n_rows == 1 && spacing.is_none() {
        return Err(CoreError::InvalidData(
            "Cannot adjust depth: DataFrame has only 1 row and spacing is \
             None (cannot calculate automatic spacing)".to_string()
        ));
    }

    let start_depth = match start_depth {
        Some(start_depth) => start_depth,
        None => {
            data.column(*COL_DEPTH)?
                .f64()?
                .get(0)
                .ok_or_else(|| CoreError::InvalidData(
                    "Cannot adjust depth: Depth column has no valid first \
                     value".to_string()
                ))?
        }
    };

    let spacing = match spacing {
        Some(spacing) => spacing,
        None => {
            let depth_series = data
                .column(*COL_DEPTH)?.clone()
                ._get_backing_series();

            let depth_diff = diff(&depth_series, 1, NullBehavior::Ignore)?;

            depth_diff.mean().ok_or_else(|| {
                CoreError::InvalidData(
                    "Cannot adjust depth: All diff values are NaN when \
                     calculating automatic spacing".to_string()
                )
            })?
        }
    };

    // round spacing to 3 decimal places
    let spacing = (spacing * 1000.0).round() / 1000.0;

    let new_depth_values: Vec<f64> = (0..n_rows)
        .map(|i| start_depth + (i as f64) * spacing)
        .collect();

    let new_depth_series = Series::new((*COL_DEPTH).into(), new_depth_values);

    let transform_expr: Vec<Expr> = data
        .get_column_names_str()
        .into_iter()
        .map(|name| {
            if name == *COL_DEPTH {
                lit(new_depth_series.clone()).alias(name)
            } else {
                col(name)
            }
        })
        .collect();

    let out_data = data
        .lazy()
        .select(transform_expr)
        .collect()?;

    Ok(out_data)
}
