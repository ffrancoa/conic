use polars::prelude::*;
use crate::kernel::CoreError;
use crate::kernel::config::{
    COL_DEPTH, COL_QC, COL_FS, COL_U2, COL_U0,
    COL_SIGV_TOT, COL_SIGV_EFF, COL_QT, COL_FR, COL_BQ,
    COL_N, COL_QTN, COL_IC, COL_CONVG,
};

/// Computes basic stress-related and normalized CPT parameters.
///
/// This function derives fundamental quantities from raw CPTu data,
/// including total and effective vertical stresses.
pub(crate) fn add_stress_cols(
    data: DataFrame,
    a_ratio: f64,
    gamma: f64
) -> Result<DataFrame, CoreError> {
    let out_data = data
        .lazy()
        // total vertical stress = γ * z
        .with_column((
                lit(gamma) * col(*COL_DEPTH)
            ).alias(*COL_SIGV_TOT)
        )
        // effective vertical stress = σv_tot - u0
        .with_column((
                col(*COL_SIGV_TOT) - col(*COL_U0)
            ).alias(*COL_SIGV_EFF)
        )
        // corrected cone resistance = qc + (1 - a) * u2
        .with_column((
                col(*COL_QC) + col(*COL_U2) * lit(1.0 - a_ratio)
                / lit(1000)
            ).alias(*COL_QT)
        )
        // normalized friction ratio = fs / (qt - σv_tot) * 100
        .with_column((
                col(*COL_FS)
                / (col(*COL_QT) * lit(1000) - col(*COL_SIGV_TOT))
                * lit(100.0)
            ).alias(*COL_FR)
        )
        // normalized pore pressure ratio = (u2 - u0) / (qt - σv_tot)
        .with_column((
                (col(*COL_U2) - col(*COL_U0))
                / (col(*COL_QT) * lit(1000) - col(*COL_SIGV_TOT))
            ).alias(*COL_BQ)
        )
        .collect()?;

    Ok(out_data)
}


/// Computes the stress exponent `n`, normalized tip resistance `Qtn`,
/// and soil behavior type index `Ic` for each CPTu record.
pub(crate) fn add_behavior_cols(
    data: DataFrame,
    max_iter: usize,
    tolerance: f64
) -> Result<DataFrame, CoreError> {
    const P_REF: f64 = 100.0;  // in kPa

    let sigv_tot = data.column(*COL_SIGV_TOT)?.f64()?;
    let sigv_eff = data.column(*COL_SIGV_EFF)?.f64()?;
    let qt = data.column(*COL_QT)?.f64()?;
    let fr = data.column(*COL_FR)?.f64()?;

    let mut n_vec = Vec::with_capacity(data.height());
    let mut qtn_vec   = Vec::with_capacity(data.height());
    let mut ic_vec    = Vec::with_capacity(data.height());
    let mut convg_vec = Vec::with_capacity(data.height());

    for i in 0..data.height() {
        let sigv_tot_i = sigv_tot.get(i).unwrap_or(f64::NAN);
        let sigv_eff_i = sigv_eff.get(i).unwrap_or(f64::NAN);
        let qt_i = qt.get(i).unwrap_or(f64::NAN) * 1000.0;  // from MPa to kPa
        let fr_i = fr.get(i).unwrap_or(f64::NAN);

        if fr_i < 0.0 || fr_i.is_nan() {
            n_vec.push(f64::NAN);
            ic_vec.push(f64::NAN);
            qtn_vec.push(f64::NAN);
            convg_vec.push(None);
            continue;
        }

        let mut convg = Some(false);
        let mut n_curr = 1.0;

        // because 'if' checks convgergence using the i + 1 term
        for _ in 0..(max_iter - 1) {
            let qtn_curr = calculate_qtn(n_curr, qt_i, sigv_eff_i, sigv_tot_i, P_REF);
            let ic_curr = calculate_ic(qtn_curr, fr_i);
            let n_next = calculate_n(ic_curr, sigv_eff_i, P_REF);

            convg = Some((n_next - n_curr).abs() <= tolerance);
            n_curr = n_next;

            if let Some(true) = convg {
                break;
            }
        }

        let n_i = n_curr;
        let qtn_i = calculate_qtn(n_i, qt_i, sigv_eff_i, sigv_tot_i, P_REF);
        let ic_i = calculate_ic(qtn_i, fr_i);

        n_vec.push(n_i);
        qtn_vec.push(qtn_i);
        ic_vec.push(ic_i);

        convg_vec.push(convg);
    }

    let out_data = data
        .lazy()
        .with_columns([
            lit(Series::new((*COL_N).into(), n_vec)),
            lit(Series::new((*COL_QTN).into(), qtn_vec)),
            lit(Series::new((*COL_IC).into(), ic_vec)),
            lit(Series::new((*COL_CONVG).into(), convg_vec)),
        ])
        .collect()?;

    Ok(out_data)
}

pub(crate) fn calculate_n(ic: f64, sigv_eff: f64, p_ref: f64) -> f64 {
    let ic_term = 0.381 * ic;
    let sigv_eff_term = 0.05 * (sigv_eff / p_ref);

    (ic_term + sigv_eff_term - 0.15).min(1.0)
}

pub(crate) fn calculate_qtn(n: f64, qt: f64, sigv_eff: f64, sigv_tot: f64, p_ref: f64) -> f64 {
    let cn = (p_ref / sigv_eff).powf(n);
    let qt_term = (qt - sigv_tot) / p_ref;

    qt_term * cn
}

pub(crate) fn calculate_ic(qtn: f64, fr: f64) -> f64 {
    let fr_term  = fr.log10() + 1.22;
    let qtn_term  = 3.47 - qtn.log10();

    (fr_term.powi(2) + qtn_term.powi(2)).sqrt()
}
