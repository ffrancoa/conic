use polars::prelude::*;
use crate::CoreError;

/// Filter out rows containing any of the given value indicators.
pub fn filter_rows(
    raw_data: DataFrame,
    filter_values: Vec<f64>,
) -> Result<DataFrame, CoreError> {
    // create list series for is_in() (polars ≥ 0.50 requirement)
    let filter_series = Series::new(PlSmallStr::from("indicators"), filter_values)
        .implode()?
        .into_series();

    let mask = all_horizontal(
        raw_data
            .get_column_names_str()
            .into_iter()
            .map(|name| col(name).is_in(lit(filter_series.clone()), false).not())
            .collect::<Vec<Expr>>(),
    )?;

    let filtered_df = raw_data
        .lazy()
        .filter(mask)
        .collect()?;

    Ok(filtered_df)
}

pub fn compute_basic(
    data: DataFrame,
    area_ratio: f64,
    gamma_soil: f64,
) -> Result<DataFrame, CoreError> {
    let out = data
        .lazy()
        // corrected cone resistance = qc + (1 - a) * u2
        .with_column(
            (
                col("qc (MPa)") + col("u2 (kPa)") * lit(1.0 - area_ratio)
                / lit(1000)
            )
            .alias("qt (MPa)")
        )
        // total vertical stress = γ * z
        .with_column(
            (lit(gamma_soil) * col("Depth (m)"))
                .alias("σv_tot (kPa)"),
        )
        // effective vertical stress = σv_tot - u0
        .with_column(
            (col("σv_tot (kPa)") - col("u0 (kPa)"))
                .alias("σv_eff (kPa)"),
        )
        // normalized friction ratio = fs / (qt - σv_tot) * 100
        .with_column(
            (
                col("fs (kPa)")
                / (col("qt (MPa)") * lit(1000) - col("σv_tot (kPa)"))
                * lit(100.0)
            )
            .alias("Fr (%)"),
        )
        // normalized pore pressure ratio = (u - u0) / (qt - σv_tot)
        .with_column(
            (
                (col("u2 (kPa)") - col("u0 (kPa)"))
                / (col("qt (MPa)") * lit(1000) - col("σv_tot (kPa)"))
            )
            .alias("Bq"),
        )
        .collect()?;

    Ok(out)
}