use serde::Deserialize;
use std::sync::{LazyLock, OnceLock};

/// Main configuration structure.
#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub columns: ColumnsConfig,
}

/// Column name configuration.
#[derive(Debug, Deserialize, Clone)]
pub struct ColumnsConfig {
    pub input: InputColumns,
    pub output: OutputColumns,
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
/// Panics if the configuration file cannot be read or parsed.
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

        toml::from_str(&config_content).unwrap_or_else(|err| {
            panic!(
                "Failed to parse configuration file '{}': {}",
                config_path, err
            )
        })
    })
}

fn input_cfg() -> &'static InputColumns {
    &config().columns.input
}

fn output_cfg() -> &'static OutputColumns {
    &config().columns.output
}

// Lazy-initialized column name constants for cleaner config access

// Input column names
pub static COL_DEPTH: LazyLock<&str> = LazyLock::new(|| &input_cfg().depth);
pub static COL_QC: LazyLock<&str> = LazyLock::new(|| &input_cfg().qc);
pub static COL_FS: LazyLock<&str> = LazyLock::new(|| &input_cfg().fs);
pub static COL_U2: LazyLock<&str> = LazyLock::new(|| &input_cfg().u2);
pub static COL_U0: LazyLock<&str> = LazyLock::new(|| &input_cfg().u0);

// Output column names
pub static COL_SIGV_TOT: LazyLock<&str> = LazyLock::new(|| &output_cfg().sigv_tot);
pub static COL_SIGV_EFF: LazyLock<&str> = LazyLock::new(|| &output_cfg().sigv_eff);
pub static COL_QT: LazyLock<&str> = LazyLock::new(|| &output_cfg().qt);
pub static COL_FR: LazyLock<&str> = LazyLock::new(|| &output_cfg().fr);
pub static COL_BQ: LazyLock<&str> = LazyLock::new(|| &output_cfg().bq);
pub static COL_N: LazyLock<&str> = LazyLock::new(|| &output_cfg().n);
pub static COL_QTN: LazyLock<&str> = LazyLock::new(|| &output_cfg().qtn);
pub static COL_IC: LazyLock<&str> = LazyLock::new(|| &output_cfg().ic);
pub static COL_CONVG: LazyLock<&str> = LazyLock::new(|| &output_cfg().convg);
pub static COL_CD: LazyLock<&str> = LazyLock::new(|| &output_cfg().cd);
pub static COL_IB: LazyLock<&str> = LazyLock::new(|| &output_cfg().ib);

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_config_loads() {
        let cfg = config();
        assert_eq!(cfg.columns.input.depth, "Depth (m)");
        assert_eq!(cfg.columns.input.qc, "qc (MPa)");
        assert_eq!(cfg.columns.output.ic, "Ic (adim.)");
    }
}
