use super::compute_qt_inv::InverseFilterParams;

const QT_FLOOR: f64 = 0.00001;

fn kernel_half_window(params: &InverseFilterParams, n: usize) -> usize {
    params.kernel_extent.map_or(n, |extent| {
        ((extent * params.dc / params.dz).ceil() as usize).min(n)
    })
}

fn calc_c1(z_prime: f64) -> f64 {
    if z_prime >= 0.0 {
        1.0
    } else {
        (1.0 + 0.125 * z_prime).max(0.5)
    }
}

fn calc_c2(z_prime: f64) -> f64 {
    if z_prime >= 0.0 { 1.0 } else { 0.8 }
}

fn calc_w2(qt_ratio: f64, mq: f64) -> f64 {
    (2.0 / (1.0 + (1.0 / qt_ratio).powf(mq))).sqrt()
}

pub(super) fn convolve(qt: &mut [f64], params: &InverseFilterParams) -> Vec<f64> {
    for value in qt.iter_mut() {
        if *value < QT_FLOOR {
            *value = QT_FLOOR;
        }
    }

    let n = qt.len();
    let hw = kernel_half_window(params, n);
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
            // i is the tip, j the soil element: z' = (z_soil - z_tip) / dc
            let z_prime = (j as f64 - i as f64) * params.dz / params.dc;
            let qt_j = qt[j];

            if qt_j <= 0.0 || qt_j.is_nan() {
                weights[k] = 0.0;
                continue;
            }

            let qt_ratio = qt_i / qt_j;
            let c1 = calc_c1(z_prime);
            let c2 = calc_c2(z_prime);

            let z50 = 1.0
                + 2.0
                    * (c2 * params.z50_ref - 1.0)
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
