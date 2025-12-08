use conic_core::{calc, io, CoreError};

fn main() -> Result<(), CoreError> {
    let err_indicators = [-9999.0, -8888.0, -7777.0];
    let gamma = 18.7;
    let a = 0.80;

    let data = io::read_csv("test/sh23-101.csv")?;
    let data = calc::clean::replace_rows(data, &err_indicators, &f64::NAN)?;
    // let data = calc::clean::remove_rows(data, &[f64::NAN])?;

    let mut out_data = calc::compute::basic_params(data, a, gamma)?;
    out_data = calc::compute::derived_params(out_data)?;

    println!("{:?}", out_data.head(Some(8)));

    Ok(())
}