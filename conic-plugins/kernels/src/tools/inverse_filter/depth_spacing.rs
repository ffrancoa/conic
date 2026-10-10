const SPACING_TOLERANCE: f64 = 0.001;

pub fn calc_dz(depth: &[f64]) -> Result<f64, String> {
    let n = depth.len();
    if n < 2 {
        return Err(format!(
            "inverse filtering requires at least 2 depth readings; got {n}"
        ));
    }

    let z_min = depth.iter().copied().fold(f64::INFINITY, f64::min);
    let z_max = depth.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let dz = (z_max - z_min) / (n - 1) as f64;

    if dz <= 0.0 {
        return Err(format!(
            "inverse filtering requires increasing depths; got a depth range of {} m",
            z_max - z_min
        ));
    }

    for (k, pair) in depth.windows(2).enumerate() {
        let step = pair[1] - pair[0];
        if step.is_nan() || (step - dz).abs() > SPACING_TOLERANCE * dz {
            return Err(format!(
                "inverse filtering requires uniformly increasing depths (relative \
                 tolerance {SPACING_TOLERANCE}); step {k} is {step} m, expected {dz} m"
            ));
        }
    }

    Ok(dz * 1000.0)
}
