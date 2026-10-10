pub(super) fn smooth_half_window(dc: f64, dz: f64) -> usize {
    let raw = (0.866 * dc / dz).ceil() as usize;
    let span = raw.max(3);
    span - 1 + span % 2
}

pub(super) fn smooth(data: &mut [f64], span: usize) {
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
