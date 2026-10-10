use crate::engine::compute_qtn::{calc_ic, calc_n, calc_qtn};

pub(super) fn correct_fs(
    qt_inv: &[f64],
    qt_meas: &[f64],
    fs: &[f64],
    fr: &[f64],
    sv_eff: &[f64],
    sv_tot: &[f64],
    p_ref: f64,
) -> Vec<f64> {
    let n = qt_inv.len();
    let mut fs_inv = Vec::with_capacity(n);

    let log_fr_center = -1.22_f64;
    let log_qtn_center = 3.47_f64;

    for i in 0..n {
        let fr_i = fr[i];

        if fr_i <= 0.0 || fr_i.is_nan() || qt_inv[i] <= 0.0 || qt_meas[i] <= 0.0 {
            fs_inv.push(fs[i]);
            continue;
        }

        let qt_inv_kpa = qt_inv[i] * 1000.0;
        let qt_meas_kpa = qt_meas[i] * 1000.0;
        let qn_inv_kpa = qt_inv_kpa - sv_tot[i];
        let fr_trial = fs[i] / qn_inv_kpa * 100.0;

        let mut n_exp = 1.0;
        for _ in 0..20 {
            let qtn_curr = calc_qtn(sv_eff[i], sv_tot[i], qt_inv_kpa, n_exp, p_ref);
            let ic_curr = calc_ic(fr_trial, qtn_curr);
            let n_next = calc_n(sv_eff[i], ic_curr, p_ref);
            if (n_next - n_exp).abs() < 1e-4 {
                n_exp = n_next;
                break;
            }
            n_exp = n_next;
        }
        let qtn_inv = calc_qtn(sv_eff[i], sv_tot[i], qt_inv_kpa, n_exp, p_ref);

        let mut n_exp_m = 1.0;
        for _ in 0..20 {
            let qtn_m = calc_qtn(sv_eff[i], sv_tot[i], qt_meas_kpa, n_exp_m, p_ref);
            let ic_m = calc_ic(fr_i, qtn_m);
            let n_next = calc_n(sv_eff[i], ic_m, p_ref);
            if (n_next - n_exp_m).abs() < 1e-4 {
                n_exp_m = n_next;
                break;
            }
            n_exp_m = n_next;
        }
        let qtn_meas = calc_qtn(sv_eff[i], sv_tot[i], qt_meas_kpa, n_exp_m, p_ref);

        let log_qtn_meas = qtn_meas.log10();
        let log_qtn_inv = qtn_inv.log10();

        let dy_meas = log_qtn_center - log_qtn_meas;
        let dx_meas = fr_i.log10() - log_fr_center;

        if dy_meas.abs() < 1e-10 {
            fs_inv.push(fs[i]);
            continue;
        }

        let k_ratio = dx_meas / dy_meas;
        let dy_inv = log_qtn_center - log_qtn_inv;
        let log_fr_inv = k_ratio * dy_inv + log_fr_center;
        let fr_inv = 10.0_f64.powf(log_fr_inv).max(0.001);

        let fs_inv_i = fr_inv / 100.0 * qn_inv_kpa;

        fs_inv.push(fs_inv_i.max(0.01));
    }

    fs_inv
}
