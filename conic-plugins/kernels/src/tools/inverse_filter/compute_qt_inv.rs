use super::convolution::convolve;
use super::fs_correction::correct_fs;
use super::interfaces::correct_interfaces;
use super::smoothing::{smooth, smooth_half_window};

#[derive(Clone, Copy)]
pub struct InverseFilterParams {
    pub dc: f64,
    pub dz: f64,
    pub z50_ref: f64,
    pub mz: f64,
    pub m50: f64,
    pub mq: f64,
    pub mt: f64,
    pub kernel_extent: Option<f64>,
    pub max_iter: usize,
    pub tolerance: f64,
}

pub struct InverseFilterResult {
    pub vec_size: usize,
    pub qt_inv: Vec<f64>,
    pub fs_inv: Vec<f64>,
    pub converged: bool,
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

pub fn compute_qt_inv(
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

    let mut qt_meas = qt.to_vec();
    let qt_conv_initial = convolve(&mut qt_meas, params);
    let qt = qt_meas.as_slice();
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
            break;
        }
        prev_err = err;

        qlast.copy_from_slice(&qt_inv);

        let qt_conv = convolve(&mut qt_inv, params);
        for i in 0..n {
            qt_inv[i] = qt[i] + (qt_inv[i] - qt_conv[i]);
        }

        smooth(&mut qt_inv, smooth_span);
    }

    let final_params = InverseFilterParams {
        z50_ref: 0.866,
        ..*params
    };
    qt_inv = convolve(&mut qt_inv, &final_params);

    if params.mt > 0.0 {
        qt_inv = correct_interfaces(&qt_inv, params);
    }

    let fs_inv = correct_fs(&qt_inv, qt, fs, fr, sv_eff, sv_tot, p_ref);

    InverseFilterResult {
        vec_size: n,
        qt_inv,
        fs_inv,
        converged,
    }
}
