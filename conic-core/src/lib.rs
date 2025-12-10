pub mod kernel;
pub mod math;
pub mod frame;

pub use kernel::{CoreError, ConicDataFrame};

/// Prelude module for convenient imports.
///
/// Import everything with:
/// ```
/// use conic_core::prelude::*;
/// ```
pub mod prelude {
    pub use crate::kernel::{ConicDataFrame, CoreError};
    pub use crate::frame::read::read_csv;
}