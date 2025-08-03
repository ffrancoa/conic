use conic_core::{io, CoreError};

fn main() -> Result<(), CoreError> {
    let df = io::read_csv("test/sh23-102.csv")?;
    println!("{:?}", df.head(Some(5)));
    Ok(())
}