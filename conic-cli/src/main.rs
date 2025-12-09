use conic_core::prelude::*;

fn main() -> Result<(), CoreError> {
    let err_indicators = [-9999.0, -8888.0, -7777.0];
    let a_ratio = 0.80;
    let gamma = 18.7;
    let max_iter = 999;
    let tolerance = 1e-3;

    let data = read_csv("data/sh23-101.csv")?
        .remove_rows(&err_indicators)?;

    let out_data = data
        .add_stress_cols(a_ratio, gamma)?
        .add_behavior_cols(max_iter, tolerance)?;

    println!("{:?}", out_data.head(Some(8)));

    Ok(())
}