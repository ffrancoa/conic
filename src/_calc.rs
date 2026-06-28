pub(crate) struct BehaviorVecs {
    pub vec_size: usize,
    pub n_vec: Vec<f64>,
    pub qtn_vec: Vec<f64>,
    pub ic_vec: Vec<f64>,
    pub convg_vec: Vec<Option<bool>>,
    pub cd_vec: Vec<f64>,
    pub ib_vec: Vec<f64>,
}

pub(crate) fn calc_n(sv_eff: f64, ic: f64, p_ref: f64) -> f64 {
    let sv_eff_term = 0.05 * (sv_eff / p_ref);
    let ic_term = 0.381 * ic;

    (ic_term + sv_eff_term - 0.15).clamp(0.0, 1.0)
}

pub(crate) fn calc_qtn(sv_eff: f64, sv_tot: f64, qt: f64, n: f64, p_ref: f64) -> f64 {
    let qt_term = (qt - sv_tot) / p_ref;
    let cn = (p_ref / sv_eff).powf(n);

    (qt_term * cn).max(0.0001)
}

pub(crate) fn calc_ic(fr: f64, qtn: f64) -> f64 {
    let fr_term = fr.log10() + 1.22;
    let qtn_term = 3.47 - qtn.log10();

    (fr_term.powi(2) + qtn_term.powi(2)).sqrt()
}

pub(crate) fn calc_cd(fr: f64, qtn: f64) -> f64 {
    let fr_term = (1.0 + 0.06 * fr).powi(17);
    let qtn_term = qtn - 11.0;

    (qtn_term * fr_term).clamp(0.0, 140.0)
}

pub(crate) fn calc_ib(fr: f64, qtn: f64) -> f64 {
    let num = qtn + 10.0;
    let den = 70.0 + qtn * fr;

    100.0 * (num / den)
}

pub(crate) fn compute_behavior(
    sv_eff: &[f64],
    sv_tot: &[f64],
    qt: &[f64],
    fr: &[f64],
    p_ref: f64,
    max_iter: usize,
    tolerance: f64,
) -> BehaviorVecs {
    let vec_size = qt.len();

    let mut ic_vec = Vec::with_capacity(vec_size);
    let mut qtn_vec = Vec::with_capacity(vec_size);
    let mut n_vec = Vec::with_capacity(vec_size);
    let mut convg_vec = Vec::with_capacity(vec_size);

    let mut cd_vec = Vec::with_capacity(vec_size);
    let mut ib_vec = Vec::with_capacity(vec_size);

    for i in 0..vec_size {
        let sv_eff_i = sv_eff[i];
        let sv_tot_i = sv_tot[i];
        let qt_i = qt[i] * 1000.0;
        let fr_i = fr[i];

        if fr_i <= 0.0 || fr_i.is_nan() {
            n_vec.push(f64::NAN);
            qtn_vec.push(f64::NAN);
            ic_vec.push(f64::NAN);
            cd_vec.push(f64::NAN);
            ib_vec.push(f64::NAN);

            convg_vec.push(None);

            continue;
        }

        let mut convg = Some(false);
        let mut n_curr = 1.0;

        for _ in 0..(max_iter - 1) {
            let qtn_curr = calc_qtn(sv_eff_i, sv_tot_i, qt_i, n_curr, p_ref);
            let ic_curr = calc_ic(fr_i, qtn_curr);
            let n_next = calc_n(sv_eff_i, ic_curr, p_ref);

            let has_convg = (n_next - n_curr).abs() <= tolerance;
            convg = Some(has_convg);

            n_curr = n_next;

            if has_convg {
                break;
            };
        }

        convg_vec.push(convg);

        let n_i = n_curr;
        let qtn_i = calc_qtn(sv_eff_i, sv_tot_i, qt_i, n_i, p_ref);
        let ic_i = calc_ic(fr_i, qtn_i);

        n_vec.push(n_i);
        qtn_vec.push(qtn_i);
        ic_vec.push(ic_i);

        cd_vec.push(calc_cd(fr_i, qtn_i));
        ib_vec.push(calc_ib(fr_i, qtn_i));
    }

    BehaviorVecs {
        vec_size,
        n_vec,
        qtn_vec,
        ic_vec,
        convg_vec,
        cd_vec,
        ib_vec,
    }
}