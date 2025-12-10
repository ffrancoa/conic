use polars::prelude::*;
use super::error::CoreError;

/// DataFrame specialized for CPTu data processing.
///
/// This wrapper provides domain-specific methods for CPTu (Cone Penetration
/// Test with pore pressure measurement) data analysis while maintaining full
/// access to underlying Polars DataFrame functionality through Deref.
pub struct ConicDataFrame(DataFrame);

impl ConicDataFrame {
    /// Creates a new ConicDataFrame from a Polars DataFrame.
    pub fn new(data: DataFrame) -> Self {
        Self(data)
    }

    /// Computes basic stress-related and normalized CPT parameters.
    ///
    /// This function derives fundamental quantities from raw CPTu data,
    /// including total and effective vertical stresses.
    pub fn add_stress_cols(
        self,
        a_ratio: Option<f64>,
        gamma: Option<f64>,
        rolling: Option<usize>
    ) -> Result<Self, CoreError> {
        let out_data = crate::math::basic::add_stress_cols(
            self.0,
            a_ratio,
            gamma,
            rolling
        )?;
        Ok(Self(out_data))
    }

    /// Computes the stress exponent `n`, normalized tip resistance `Qtn`,
    /// and soil behavior type index `Ic` for each CPTu record.
    pub fn add_behavior_cols(
        self,
        max_iter: Option<usize>,
        tolerance: Option<f64>
    ) -> Result<Self, CoreError> {
        let out_data = crate::math::basic::add_behavior_cols(
            self.0,
            max_iter,
            tolerance
        )?;
        Ok(Self(out_data))
    }

    /// Removes rows containing any of the specified indicator values.
    ///
    /// A row is eliminated if ANY column contains ANY value from the
    /// indicators list.
    pub fn remove_rows(self, indicators: &[f64]) -> Result<Self, CoreError> {
        let out_data = crate::frame::clean::remove_rows(
            self.0,
            indicators
        )?;
        Ok(Self(out_data))
    }

    /// Replaces values in rows containing indicator values.
    ///
    /// When a row has ANY column containing ANY value from the indicators
    /// list, ALL values in that row (except depth) are replaced with
    /// `replace_value`. This preserves depth information while marking
    /// invalid measurements.
    pub fn replace_rows(
        self,
        indicators: &[f64],
        replace_value: &f64,
    ) -> Result<Self, CoreError> {
        let out_data = crate::frame::clean::replace_rows(
            self.0,
            indicators,
            replace_value
        )?;
        Ok(Self(out_data))
    }

    /// Consumes the wrapper and returns the inner DataFrame.
    pub fn into_inner(self) -> DataFrame {
        self.0
    }

    /// Returns a reference to the inner DataFrame.
    pub fn inner(&self) -> &DataFrame {
        &self.0
    }

    /// Returns a mutable reference to the inner DataFrame.
    pub fn inner_mut(&mut self) -> &mut DataFrame {
        &mut self.0
    }
}

impl std::ops::Deref for ConicDataFrame {
    type Target = DataFrame;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl std::ops::DerefMut for ConicDataFrame {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

impl From<DataFrame> for ConicDataFrame {
    fn from(df: DataFrame) -> Self {
        Self(df)
    }
}

impl From<ConicDataFrame> for DataFrame {
    fn from(conic: ConicDataFrame) -> Self {
        conic.0
    }
}
