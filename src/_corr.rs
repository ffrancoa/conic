pub(crate) struct Qc1nVecs {
    pub vec_size: usize,
    pub m_vec: Vec<f64>,
    pub qc1n_vec: Vec<f64>,
    pub qc1ncs_vec: Vec<f64>,
    pub convg_vec: Vec<Option<bool>>,
}

pub(crate) fn calc_ns(qc1ncs: f64) -> f64 {
    1.338 - 0.249 * qc1ncs.powf(0.264)
}

pub(crate) fn calc_cn(sv_eff: f64, m: f64, p_ref: f64) -> f64 {
    let sv_eff_term = (p_ref / sv_eff).powf(m);

    sv_eff_term.min(1.7)
}

pub(crate) fn compute_qc1n(
    sv_eff: &[f64],
    qt: &[f64],
    fc: &[f64],
    p_ref: f64,
    max_iter: usize,
    tolerance: f64,
) -> Qc1nVecs {
    let vec_size = qt.len();

    let mut m_vec = Vec::with_capacity(vec_size);
    let mut qc1n_vec = Vec::with_capacity(vec_size);
    let mut qc1ncs_vec = Vec::with_capacity(vec_size);
    let mut convg_vec = Vec::with_capacity(vec_size);

    for i in 0..vec_size {
        let sv_eff_i = sv_eff[i];
        let qt_i = qt[i] * 1000.0;
        let fc_i = fc[i];

        if qt_i.is_nan() {
            m_vec.push(f64::NAN);
            qc1n_vec.push(f64::NAN);
            qc1ncs_vec.push(f64::NAN);
            convg_vec.push(None);

            continue;
        }

        let fc_shifted = fc_i + 2.0;
        let exp_term = (1.63 - 9.7 / fc_shifted - (15.7 / fc_shifted).powi(2)).exp();

        let mut convg = Some(false);
        let mut m_curr = 0.5;

        for _ in 0..max_iter {
            let cn = calc_cn(sv_eff_i, m_curr, p_ref);
            let qc1n = cn * qt_i / p_ref;
            let qc1ncs = qc1n + (11.9 + qc1n / 14.6) * exp_term;

            let m_next = calc_ns(qc1ncs);

            if (m_next - m_curr).abs() <= tolerance {
                m_curr = m_next;
                convg = Some(true);
                break;
            }

            m_curr = m_next;
        }

        convg_vec.push(convg);

        let m_i = m_curr;
        let cn = calc_cn(sv_eff_i, m_i, p_ref);
        let qc1n_i = cn * qt_i / p_ref;
        let qc1ncs_i = qc1n_i + (11.9 + qc1n_i / 14.6) * exp_term;

        m_vec.push(m_i);
        qc1n_vec.push(qc1n_i);
        qc1ncs_vec.push(qc1ncs_i);
    }

    Qc1nVecs {
        vec_size,
        m_vec,
        qc1n_vec,
        qc1ncs_vec,
        convg_vec,
    }
}
