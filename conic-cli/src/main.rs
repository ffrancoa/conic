use conic_core::{calc, io, CoreError};

fn main() -> Result<(), CoreError> {
    let df = io::read_csv("test/sh23-104.csv")?;
    let indicators = vec![-9999.0, -8888.0, -7777.0];
    let clean_df = calc::filter_value_rows(df, indicators)?;
    println!("{:?}", clean_df.head(Some(5)));
    Ok(())
}