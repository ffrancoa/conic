use super::compute_qt_inv::InverseFilterParams;

pub(super) fn correct_interfaces(
    qt_inv: &[f64],
    params: &InverseFilterParams,
) -> Vec<f64> {
    let n = qt_inv.len();
    let mut qt_corrected = qt_inv.to_vec();

    let dz_norm = params.dz / params.dc;
    let rate_lim = params.mt;
    let rate_enter = rate_lim / 5.0;

    let grad: Vec<f64> = qt_inv
        .windows(2)
        .map(|pair| (pair[1] / pair[0]).ln() / dz_norm)
        .collect();

    let mut zone: Option<(usize, bool)> = None;
    for i in 0..grad.len() {
        let Some((zone_start, increasing)) = zone else {
            if grad[i].abs() > rate_enter {
                zone = Some((i, grad[i] > 0.0));
            }
            continue;
        };

        let direction = if increasing { 1.0 } else { -1.0 };
        if direction * grad[i] > rate_enter {
            continue;
        }
        zone = None;

        let zone_end = i;
        let peak = grad[zone_start..zone_end]
            .iter()
            .map(|g| direction * g)
            .fold(f64::NEG_INFINITY, f64::max);
        if peak < rate_lim {
            continue;
        }

        let zone_width = (zone_end - zone_start) as f64 * dz_norm;
        if zone_width <= 3.0 {
            continue;
        }

        let (max_width, split_frac) =
            if increasing { (12.0, 0.4) } else { (18.0, 0.6) };
        let (mut top, mut bottom) = (zone_start, zone_end);
        if zone_width > max_width {
            let center = (zone_start + zone_end) / 2;
            let clip_half = (0.5 * max_width / dz_norm) as usize;
            top = center.saturating_sub(clip_half);
            bottom = (center + clip_half).min(n - 1);
        }

        let split = top as f64 + split_frac * (bottom - top) as f64;
        for (j, cell) in qt_corrected.iter_mut().enumerate().take(bottom).skip(top) {
            *cell = if j as f64 <= split {
                qt_inv[top]
            } else {
                qt_inv[bottom]
            };
        }
    }

    qt_corrected
}
