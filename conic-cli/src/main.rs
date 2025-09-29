use conic_core::{calc, io, CoreError};

fn main() -> Result<(), CoreError> {
    let filter_values = vec![-9999.0, -8888.0, -7777.0];
    let gamma = 18.7;
    let a = 0.80;

    let df = io::read_csv("test/sh23-104.csv")?;
    let clean_df = calc::filter_rows(df, filter_values)?;
    let out_df = calc::compute_basic(clean_df, a, gamma)?;

    println!("{:?}", out_df.head(Some(8)));

    Ok(())
}