use conic_core::{calc, io, CoreError};

fn main() -> Result<(), CoreError> {
    let df = io::read_csv("test/sh23-102.csv")?;
    let null_indicators = vec![-9999.0, -8888.0, -7777.0];
    let clean_df = calc::drop_value_rows(df, null_indicators)?;
    println!("{:?}", clean_df.head(Some(5)));
    Ok(())
}