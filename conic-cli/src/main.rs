use conic_core::{calc, io, CoreError};

fn main() -> Result<(), CoreError> {
    let filter_values = vec![-9999.0, -8888.0, -7777.0];
    let gamma = 18.7;
    let a = 0.80;

    let df = io::read_csv("test/sh23-101.csv")?;
    let clean_df = calc::clean::filter_rows(df, filter_values)?;
    let mut out_df = calc::compute::basic_params(clean_df, a, gamma)?;
    out_df = calc::compute::derived_params(out_df)?;

    println!("{:?}", out_df.head(Some(8)));

    Ok(())
}