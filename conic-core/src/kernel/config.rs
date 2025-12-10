use serde::Deserialize;
use std::sync::{LazyLock, OnceLock};
use super::CoreError;

/// Main configuration structure.
#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub input: InputConfig,
    pub output: OutputConfig,
}

/// Input configuration.
#[derive(Debug, Deserialize, Clone)]
pub struct InputConfig {
    pub parameters: InputParameters,
    pub columns: InputColumns,
}

/// Output configuration.
#[derive(Debug, Deserialize, Clone)]
pub struct OutputConfig {
    pub parameters: OutputParameters,
    pub columns: OutputColumns,
}

/// Input parameters for CPTu calculations.
#[derive(Debug, Deserialize, Clone)]
pub struct InputParameters {
    pub a_ratio: f64,
    pub gamma_w: f64,
    pub gamma_s: f64,
    pub p_ref: f64,
    pub rolling: usize,
}

/// Output parameters for iterative calculations.
#[derive(Debug, Deserialize, Clone)]
pub struct OutputParameters {
    pub max_iter: usize,
    pub tolerance: f64,
}

/// Input column names (from CSV).
#[derive(Debug, Deserialize, Clone)]
pub struct InputColumns {
    pub depth: String,
    pub qc: String,
    pub fs: String,
    pub u2: String,
    pub u0: String
}

/// Output column names (derived parameters).
#[derive(Debug, Deserialize, Clone)]
pub struct OutputColumns {
    pub sigv_tot: String,
    pub sigv_eff: String,
    pub qt: String,
    pub fr: String,
    pub bq: String,
    pub n: String,
    pub qtn: String,
    pub ic: String,
    pub convg: String,
    pub cd: String,
    pub ib: String
}

/// Global configuration instance.
static CONFIG: OnceLock<Config> = OnceLock::new();

/// Loads and returns the global configuration.
///
/// The configuration is loaded once from `config.toml` and cached.
/// Subsequent calls return the cached configuration.
///
/// # Panics
/// Panics if the configuration file cannot be read, parsed, or contains
/// invalid values.
fn config() -> &'static Config {
    CONFIG.get_or_init(|| {
        let config_path = "conic-core/config.toml";
        let config_content = std::fs::read_to_string(config_path)
            .unwrap_or_else(|err| {
                panic!(
                    "Failed to read configuration file '{}': {}",
                    config_path, err
                )
            });

        let cfg: Config = toml::from_str(&config_content).unwrap_or_else(|err| {
            panic!(
                "Failed to parse configuration file '{}': {}",
                config_path, err
            )
        });

        // validate configuration
        validate_config(&cfg).unwrap_or_else(|err| {
            panic!("{}", err)
        });

        cfg
    })
}

/// Validates the loaded configuration.
fn validate_config(cfg: &Config) -> Result<(), CoreError> {
    // validate rolling parameter
    if ![1, 3, 5].contains(&cfg.input.parameters.rolling) {
        return Err(CoreError::InvalidConfig(
            format!(
                "Invalid rolling parameter: {}. Must be 1, 3, or 5",
                cfg.input.parameters.rolling
            )
        ));
    }

    Ok(())
}

fn input_cols() -> &'static InputColumns {
    &config().input.columns
}

fn output_cols() -> &'static OutputColumns {
    &config().output.columns
}

fn input_params() -> &'static InputParameters {
    &config().input.parameters
}

fn output_params() -> &'static OutputParameters {
    &config().output.parameters
}

// Lazy-initialized column name constants for cleaner config access

// Input column names
pub static COL_DEPTH: LazyLock<&str> = LazyLock::new(|| &input_cols().depth);
pub static COL_QC: LazyLock<&str> = LazyLock::new(|| &input_cols().qc);
pub static COL_FS: LazyLock<&str> = LazyLock::new(|| &input_cols().fs);
pub static COL_U2: LazyLock<&str> = LazyLock::new(|| &input_cols().u2);
pub static COL_U0: LazyLock<&str> = LazyLock::new(|| &input_cols().u0);

// Output column names
pub static COL_SIGV_TOT: LazyLock<&str> = LazyLock::new(|| &output_cols().sigv_tot);
pub static COL_SIGV_EFF: LazyLock<&str> = LazyLock::new(|| &output_cols().sigv_eff);
pub static COL_QT: LazyLock<&str> = LazyLock::new(|| &output_cols().qt);
pub static COL_FR: LazyLock<&str> = LazyLock::new(|| &output_cols().fr);
pub static COL_BQ: LazyLock<&str> = LazyLock::new(|| &output_cols().bq);
pub static COL_N: LazyLock<&str> = LazyLock::new(|| &output_cols().n);
pub static COL_QTN: LazyLock<&str> = LazyLock::new(|| &output_cols().qtn);
pub static COL_IC: LazyLock<&str> = LazyLock::new(|| &output_cols().ic);
pub static COL_CONVG: LazyLock<&str> = LazyLock::new(|| &output_cols().convg);
pub static COL_CD: LazyLock<&str> = LazyLock::new(|| &output_cols().cd);
pub static COL_IB: LazyLock<&str> = LazyLock::new(|| &output_cols().ib);

// Input parameters
pub static A_RATIO: LazyLock<f64> = LazyLock::new(|| input_params().a_ratio);
pub static GAMMA_S: LazyLock<f64> = LazyLock::new(|| input_params().gamma_s);
pub static P_REF: LazyLock<f64> = LazyLock::new(|| input_params().p_ref);
pub static ROLLING: LazyLock<usize> = LazyLock::new(|| input_params().rolling);

// Output parameters
pub static MAX_ITER: LazyLock<usize> =
    LazyLock::new(|| output_params().max_iter);
pub static TOLERANCE: LazyLock<f64> =
    LazyLock::new(|| output_params().tolerance);
