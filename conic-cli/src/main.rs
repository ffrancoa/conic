use conic_core::prelude::*;

fn main() -> Result<(), CoreError> {
    let err_indicators = [-9999.0, -8888.0, -7777.0];

    let data = read_csv("data/sh23-101.csv")?
        .replace_rows(&err_indicators, &f64::NAN)?
        .adjust_depth(Some(0.125), None)?
        .remove_rows(&[f64::NAN])?;

    let out_data = data
        .add_stress_cols(None, None, None)?
        .add_behavior_cols(None, None)?;

    println!("{:?}", out_data.head(Some(8)));

    Ok(())
}