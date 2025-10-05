use polars::prelude::*;
use crate::CoreError;


/// Computes basic stress-related and normalized CPT parameters.
///
/// This function derives fundamental quantities from raw CPTu data,
/// including total and effective vertical stresses.
pub fn basic_params(
    data: DataFrame,
    area_ratio: f64,
    gamma_soil: f64,
) -> Result<DataFrame, CoreError> {
    let out = data.lazy()
        // total vertical stress = γ * z
        .with_column(
            (lit(gamma_soil) * col("Depth (m)"))
                .alias("σv_tot (kPa)"),
        )
        // effective vertical stress = σv_tot - u0
        .with_column(
            (col("σv_tot (kPa)") - col("u0 (kPa)"))
                .alias("σv_eff (kPa)"),
        )
        // corrected cone resistance = qc + (1 - a) * u2
        .with_column(
            (
                col("qc (MPa)") + col("u2 (kPa)") * lit(1.0 - area_ratio)
                / lit(1000)
            )
            .alias("qt (MPa)")
        )
        // normalized friction ratio = fs / (qt - σv_tot) * 100
        .with_column(
            (
                col("fs (kPa)")
                / (col("qt (MPa)") * lit(1000) - col("σv_tot (kPa)"))
                * lit(100.0)
            )
            .alias("Fr (%)"),
        )
        // normalized pore pressure ratio = (u2 - u0) / (qt - σv_tot)
        .with_column(
            (
                (col("u2 (kPa)") - col("u0 (kPa)"))
                / (col("qt (MPa)") * lit(1000) - col("σv_tot (kPa)"))
            )
            .alias("Bq"),
        )
        .collect()?;

    Ok(out)
}


/// Computes the stress exponent `n`, normalized tip resistance `Qtn`,
/// and soil behavior type index `Ic` for each CPTu record.
pub fn derived_params(mut df: DataFrame) -> Result<DataFrame, CoreError> {
    const P_REF: f64 = 100.0;  // in kPa
    const MAX_ITER: usize = 999;
    const TOLERANCE: f64 = 1e-3;

    let sigv_t = df.column("σv_tot (kPa)")?.f64()?;
    let sigv_e = df.column("σv_eff (kPa)")?.f64()?;
    let qt = df.column("qt (MPa)")?.f64()?;
    let fr = df.column("Fr (%)")?.f64()?;

    let mut n_vec = Vec::with_capacity(df.height());
    let mut qtn_vec   = Vec::with_capacity(df.height());
    let mut ic_vec    = Vec::with_capacity(df.height());
    let mut status_vec = Vec::with_capacity(df.height());

    for i in 0..df.height() {
        let sigv_t_i = sigv_t.get(i).unwrap_or(f64::NAN);
        let sigv_e_i = sigv_e.get(i).unwrap_or(f64::NAN);
        let qt_i = qt.get(i).unwrap_or(f64::NAN) * 1000.0; // from MPa to kPa
        let fr_i = fr.get(i).unwrap_or(f64::NAN);

        if fr_i < 0.0 {
            n_vec.push(f64::NAN);
            ic_vec.push(f64::NAN);
            qtn_vec.push(f64::NAN);
            status_vec.push(true);
            continue;
        }

        let mut converged = false;
        let mut n_curr = 1.0;

        // because 'if' checks convergence using the i + 1 term
        for _ in 0..(MAX_ITER - 1) {
            let qtn_curr = calc_qtn(n_curr, qt_i, sigv_e_i, sigv_t_i, P_REF);
            let ic_curr = calc_ic(qtn_curr, fr_i);
            let n_next = calc_n(ic_curr, sigv_e_i, P_REF);

            converged = (n_next - n_curr).abs() <= TOLERANCE;
            n_curr = n_next;

            if converged {
                break;
            }
        }

        let n_i = n_curr;
        let qtn_i = calc_qtn(n_i, qt_i, sigv_e_i, sigv_t_i, P_REF);
        let ic_i = calc_ic(qtn_i, fr_i);

        n_vec.push(n_i);
        qtn_vec.push(qtn_i);
        ic_vec.push(ic_i);

        status_vec.push(converged);
    }

    df.with_column(Series::new("n_exp".into(), n_vec))?;
    df.with_column(Series::new("Qtn".into(), qtn_vec))?;
    df.with_column(Series::new("Ic".into(), ic_vec))?;
    df.with_column(Series::new("status".into(), status_vec))?;

    Ok(df)
}

fn calc_n(ic: f64, sigv_e: f64, p_ref: f64) -> f64 {
    let term_ic = 0.381 * ic;
    let term_sigv_e = 0.05 * (sigv_e / p_ref);

    (term_ic + term_sigv_e - 0.15).min(1.0)
}

fn calc_qtn(n: f64, qt: f64, sigv_e: f64, sigv_t: f64, p_ref: f64) -> f64 {
    let cn = (p_ref / sigv_e).powf(n);
    let term_qt = (qt - sigv_t) / p_ref;

    term_qt * cn
}

fn calc_ic(qtn: f64, fr: f64) -> f64 {
    let log_qtn = qtn.log10();
    let log_fr = fr.log10();

    let term_qtn  = 3.47 - log_qtn;
    let term_fr  = log_fr + 1.22;

    (term_qtn.powi(2) + term_fr.powi(2)).sqrt()
}