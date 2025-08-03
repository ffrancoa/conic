use std::fmt;
use std::error::Error;
use polars::error::PolarsError;

/// Generic error.
#[derive(Debug)]
pub enum CoreError {
    Io(std::io::Error),
    Polars(PolarsError),
    InvalidData(String),
}

impl fmt::Display for CoreError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CoreError::Io(e) => write!(f, "I/O error: {e}"),
            CoreError::Polars(e) => write!(f, "Polars error: {e}"),
            CoreError::InvalidData(msg) => write!(f, "Invalid data: {msg}"),
        }
    }
}

impl Error for CoreError {}

/// Conversión automática de `std::io::Error` → `CoreError`
impl From<std::io::Error> for CoreError {
    fn from(err: std::io::Error) -> Self {
        CoreError::Io(err)
    }
}

/// Conversión automática de `polars::error::PolarsError` → `CoreError`
impl From<PolarsError> for CoreError {
    fn from(err: PolarsError) -> Self {
        CoreError::Polars(err)
    }
}
