use thiserror::Error;
use polars::error::PolarsError;

/// Generic error.
#[derive(Debug, Error)]
pub enum CoreError {
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Polars error: {0}")]
    Polars(#[from] PolarsError),

    #[error("Invalid data: {0}")]
    InvalidData(String),
}