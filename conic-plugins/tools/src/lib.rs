use conic_processing::{calc_ic, calc_n, calc_qtn};

#[derive(Clone, Copy)]
#[allow(dead_code)]
pub struct InverseFilterParams {
    pub dc: f64,
    pub dz: f64,
    pub z50_ref: f64,
    pub mz: f64,
    pub m50: f64,
    pub mq: f64,
    pub mt: f64,
    pub max_iter: usize,
    pub tolerance: f64,
    pub stall_tolerance: f64,
}

pub struct InverseFilterResult {
    pub vec_size: usize,
    pub qt_inv: Vec<f64>,
    pub fs_inv: Vec<f64>,
    pub converged: bool,
}

fn kernel_half_window(dc: f64, dz: f64) -> usize {
    (30.0 * dc / dz).ceil() as usize
}

fn smooth_half_window(dc: f64, dz: f64) -> usize {
    let raw = (0.866 * dc / dz).ceil() as usize;
    let span = raw.max(3);
    span - 1 + span % 2
}

fn calc_c1(z_prime: f64) -> f64 {
    if z_prime <= 0.0 {
        1.0
    } else {
        (1.0 - 0.125 * z_prime).max(0.5)
    }
}

fn calc_c2(z_prime: f64) -> f64 {
    if z_prime <= 0.0 {
        1.0
    } else {
        0.8
    }
}

fn calc_w2(qt_ratio: f64, mq: f64) -> f64 {
    (2.0 / (1.0 + (1.0 / qt_ratio).powf(mq))).sqrt()
}

fn convolve(qt: &[f64], params: &InverseFilterParams) -> Vec<f64> {
    let n = qt.len();
    let hw = kernel_half_window(params.dc, params.dz);
    let buf_size = 2 * hw + 1;
    let mut weights = vec![0.0; buf_size];
    let mut result = vec![0.0; n];

    for i in 0..n {
        let qt_i = qt[i];
        if qt_i <= 0.0 || qt_i.is_nan() {
            result[i] = qt_i;
            continue;
        }

        let j_start = i.saturating_sub(hw);
        let j_end = (i + hw + 1).min(n);
        let count = j_end - j_start;

        let mut sum_w = 0.0;

        for (k, j) in (j_start..j_end).enumerate() {
            let z_prime = (j as f64 - i as f64) * params.dz / params.dc;
            let qt_j = qt[j];

            if qt_j <= 0.0 || qt_j.is_nan() {
                weights[k] = 0.0;
                continue;
            }

            let qt_ratio = qt_j / qt_i;
            let c1 = calc_c1(z_prime);
            let c2 = calc_c2(z_prime);

            let z50 = 1.0
                + 2.0 * (c2 * params.z50_ref - 1.0)
                    * (1.0 - 1.0 / (1.0 + qt_ratio.powf(params.m50)));

            let w1 = c1 / (1.0 + (z_prime.abs() / z50).powf(params.mz));
            let w2 = calc_w2(qt_ratio, params.mq);

            let w = w1 * w2;
            weights[k] = w;
            sum_w += w;
        }

        if sum_w > 0.0 {
            let mut val = 0.0;
            for (k, j) in (j_start..j_end).enumerate() {
                val += qt[j] * weights[k] / sum_w;
            }
            result[i] = val;
        } else {
            result[i] = qt_i;
        }

        for w in weights.iter_mut().take(count) {
            *w = 0.0;
        }
    }

    result
}

fn smooth(data: &mut [f64], span: usize) {
    let n = data.len();
    if span <= 1 || n <= 1 {
        return;
    }

    let tmp = data.to_vec();
    let half = (span - 1) / 2;

    for (idx, sample) in data.iter_mut().enumerate().take(n) {
        let sub_half = half.min(idx).min(n - 1 - idx);
        let start = idx - sub_half;
        let end = idx + sub_half + 1;
        let sum: f64 = tmp[start..end].iter().sum();
        *sample = sum / (end - start) as f64;
    }
}

fn calc_initial_estimate(qt_measured: &[f64], qt_convolved: &[f64]) -> Vec<f64> {
    let n = qt_measured.len();
    let mut estimate = Vec::with_capacity(n);

    for i in 0..n {
        let floor = 0.5 * qt_measured[i];
        let boost = 2.0 * qt_measured[i] - qt_convolved[i];
        estimate.push(floor.max(boost));
    }

    estimate
}

fn correct_interfaces(qt_inv: &mut [f64], params: &InverseFilterParams) {
    let n = qt_inv.len();
    if n < 3 {
        return;
    }

    let dz_norm = params.dz / params.dc;
    let rate_lim = params.mt;
    let rate_enter = rate_lim / 5.0;

    let max_zone_inc = (12.0 / dz_norm).ceil() as usize;
    let max_zone_dec = (18.0 / dz_norm).ceil() as usize;

    let mut grad = vec![0.0f64; n - 1];
    for i in 0..n - 1 {
        if qt_inv[i] > 0.0 && qt_inv[i + 1] > 0.0 {
            grad[i] = (qt_inv[i + 1].ln() - qt_inv[i].ln()) / dz_norm;
        }
    }

    let mut i = 0;
    while i < n - 1 {
        if grad[i].abs() <= rate_enter {
            i += 1;
            continue;
        }

        let zone_start = i;
        let increasing = grad[i] > 0.0;
        let mut qualified = grad[i].abs() > rate_lim;

        let max_zone = if increasing { max_zone_inc } else { max_zone_dec };

        let mut j = i + 1;
        while j < n - 1 && (j - zone_start) < max_zone {
            if grad[j].abs() <= rate_enter {
                break;
            }
            if (grad[j] > 0.0) != increasing {
                break;
            }
            if grad[j].abs() > rate_lim {
                qualified = true;
            }
            j += 1;
        }

        let zone_end = j;
        let zone_width = zone_end - zone_start;

        if qualified && zone_width >= 2 {
            let center = (zone_start + zone_end) / 2;
            let clip_half = max_zone / 2;
            let clipped_start = center.saturating_sub(clip_half)
            .max(zone_start);
            let clipped_end = (center + clip_half).min(n).min(zone_end + 1);

            let val_before = qt_inv[clipped_start];
            let val_after = if clipped_end < n {
                qt_inv[clipped_end]
            } else {
                qt_inv[n - 1]
            };

            let split_frac = if increasing { 0.4 } else { 0.6 };
            let split_idx =
                clipped_start + ((clipped_end - clipped_start) as f64 * split_frac) as usize;

            for cell in qt_inv.iter_mut().take(split_idx).skip(clipped_start) {
                *cell = val_before;
            }
            for cell in qt_inv.iter_mut().take(clipped_end.min(n)).skip(split_idx) {
                *cell = val_after;
            }
        }

        i = zone_end;
    }
}

fn correct_fs(
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

        let mut n_exp = 1.0;
        for _ in 0..20 {
            let qtn_curr = calc_qtn(sv_eff[i], sv_tot[i], qt_inv_kpa, n_exp, p_ref);
            let ic_curr = calc_ic(fr_i, qtn_curr);
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

        let qn_inv_kpa = qt_inv_kpa - sv_tot[i];
        let fs_inv_i = fr_inv / 100.0 * qn_inv_kpa;

        fs_inv.push(fs_inv_i.max(0.01));
    }

    fs_inv
}

pub fn inverse_filter(
    qt: &[f64],
    fs: &[f64],
    fr: &[f64],
    sv_eff: &[f64],
    sv_tot: &[f64],
    p_ref: f64,
    params: &InverseFilterParams,
) -> InverseFilterResult {
    let n = qt.len();
    let smooth_span = smooth_half_window(params.dc, params.dz);

    let qt_conv_initial = convolve(qt, params);
    let mut qt_inv = calc_initial_estimate(qt, &qt_conv_initial);

    let qt_sum: f64 = qt.iter().map(|v| v.abs()).sum();

    if qt_sum <= 0.0 {
        return InverseFilterResult {
            vec_size: n,
            qt_inv: qt.to_vec(),
            fs_inv: fs.to_vec(),
            converged: false,
        };
    }

    let mut qlast = qt.to_vec();
    let mut prev_err = f64::MAX;
    let mut converged = false;

    for _ in 0..params.max_iter {
        let mut diff_sum = 0.0;
        for i in 0..n {
            diff_sum += (qt_inv[i] - qlast[i]).abs();
        }
        let err = diff_sum / qt_sum;

        if err < params.tolerance {
            converged = true;
            break;
        }
        if (err - prev_err).abs() < params.tolerance {
            converged = true;
            break;
        }
        prev_err = err;

        qlast.copy_from_slice(&qt_inv);

        let qt_conv = convolve(&qt_inv, params);
        for i in 0..n {
            qt_inv[i] = qt[i] + (qt_inv[i] - qt_conv[i]);
        }

        smooth(&mut qt_inv, smooth_span);
    }

    let final_params = InverseFilterParams {
        z50_ref: 0.866,
        ..*params
    };
    qt_inv = convolve(&qt_inv, &final_params);

    if params.mt > 0.0 {
        correct_interfaces(&mut qt_inv, params);
    }

    let fs_inv = correct_fs(&qt_inv, qt, fs, fr, sv_eff, sv_tot, p_ref);

    InverseFilterResult {
        vec_size: n,
        qt_inv,
        fs_inv,
        converged,
    }
}
