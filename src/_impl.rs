#![allow(clippy::unused_unit)]
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;

use super::_calc;

#[derive(Deserialize)]
struct BehaviorKwargs {
    p_ref: f64,
    max_iter: usize,
    tolerance: f64,
}

fn compute_behavior_output(_input_fields: &[Field]) -> PolarsResult<Field> {
    let fields = vec![
        Field::new("n".into(), DataType::Float64),
        Field::new("qtn".into(), DataType::Float64),
        Field::new("ic".into(), DataType::Float64),
        Field::new("convg".into(), DataType::Boolean),
    ];

    Ok(Field::new("series_output".into(), DataType::Struct(fields)))
}

#[polars_expr(output_type_func=compute_behavior_output)]
fn compute_behavior(inputs: &[Series], kwargs: BehaviorKwargs) -> PolarsResult<Series> {
    let sv_eff_chunked = inputs[0].f64()?;
    let sv_eff_slice = sv_eff_chunked.cont_slice()?;

    let sv_tot_chunked = inputs[1].f64()?;
    let sv_tot_slice = sv_tot_chunked.cont_slice()?;

    let qt_chunked = inputs[2].f64()?;
    let qt_slice = qt_chunked.cont_slice()?;

    let fr_chunked = inputs[3].f64()?;
    let fr_slice = fr_chunked.cont_slice()?;

    let behaviour_vecs = _calc::compute_behavior(
        sv_eff_slice,
        sv_tot_slice,
        qt_slice,
        fr_slice,
        kwargs.p_ref,
        kwargs.max_iter,
        kwargs.tolerance,
    );

    let n_series = Series::new("n".into(), behaviour_vecs.n_vec);
    let qtn_series = Series::new("qtn".into(), behaviour_vecs.qtn_vec);
    let ic_series = Series::new("ic".into(), behaviour_vecs.ic_vec);
    let convg_series = Series::new("convg".into(), behaviour_vecs.convg_vec);

    let struct_chunked = StructChunked::from_series(
        "series_output".into(),
        behaviour_vecs.vec_size,
        [&n_series, &qtn_series, &ic_series, &convg_series].into_iter(),
    )?;

    Ok(struct_chunked.into_series())
}
