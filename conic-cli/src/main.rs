use conic_core::{calc, io, CoreError};

fn main() -> Result<(), CoreError> {
    let df = io::read_csv("test/sh23-102.csv")?;
    let na_indicators = [-9999.0, -8888.0, -7777.0].to_vec();
    let clean_df = calc::drop_value_rows(df, na_indicators)?;
    println!("{:?}", clean_df.head(Some(5)));
    Ok(())
}