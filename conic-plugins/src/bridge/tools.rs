use conic_kernels::tools::inverse_filter;
use conic_kernels::tools::inverse_filter::compute_qt_inv;
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;

#[derive(Deserialize)]
struct InverseFilterKwargs {
    dc: f64,
    z50_ref: f64,
    mz: f64,
    m50: f64,
    mq: f64,
    mt: f64,
    kernel_extent: Option<f64>,
    p_ref: f64,
    max_iter: usize,
    tolerance: f64,
}

fn compute_qt_inv_output(_input_fields: &[Field]) -> PolarsResult<Field> {
    let fields = vec![
        Field::new("qt_inv".into(), DataType::Float64),
        Field::new("fs_inv".into(), DataType::Float64),
        Field::new("converged".into(), DataType::Boolean),
    ];

    Ok(Field::new("series_output".into(), DataType::Struct(fields)))
}

#[polars_expr(output_type_func=compute_qt_inv_output)]
fn compute_qt_inv(
    inputs: &[Series],
    kwargs: InverseFilterKwargs,
) -> PolarsResult<Series> {
    let depth_chunked = inputs[0].f64()?.rechunk();
    let depth_slice = depth_chunked.cont_slice()?;

    let qt_chunked = inputs[1].f64()?.rechunk();
    let qt_slice = qt_chunked.cont_slice()?;

    let fs_chunked = inputs[2].f64()?.rechunk();
    let fs_slice = fs_chunked.cont_slice()?;

    let fr_chunked = inputs[3].f64()?.rechunk();
    let fr_slice = fr_chunked.cont_slice()?;

    let sv_eff_chunked = inputs[4].f64()?.rechunk();
    let sv_eff_slice = sv_eff_chunked.cont_slice()?;

    let sv_tot_chunked = inputs[5].f64()?.rechunk();
    let sv_tot_slice = sv_tot_chunked.cont_slice()?;

    let dz = inverse_filter::calc_dz(depth_slice)
        .map_err(|msg| polars_err!(ComputeError: "{}", msg))?;

    let params = compute_qt_inv::InverseFilterParams {
        dc: kwargs.dc,
        dz,
        z50_ref: kwargs.z50_ref,
        mz: kwargs.mz,
        m50: kwargs.m50,
        mq: kwargs.mq,
        mt: kwargs.mt,
        kernel_extent: kwargs.kernel_extent,
        max_iter: kwargs.max_iter,
        tolerance: kwargs.tolerance,
    };

    let result = compute_qt_inv::compute_qt_inv(
        qt_slice,
        fs_slice,
        fr_slice,
        sv_eff_slice,
        sv_tot_slice,
        kwargs.p_ref,
        &params,
    );

    let qt_inv_series = Series::new("qt_inv".into(), result.qt_inv);
    let fs_inv_series = Series::new("fs_inv".into(), result.fs_inv);
    let converged_vec: Vec<Option<bool>> =
        vec![Some(result.converged); result.vec_size];
    let converged_series = Series::new("converged".into(), converged_vec);

    let struct_chunked = StructChunked::from_series(
        "series_output".into(),
        result.vec_size,
        [&qt_inv_series, &fs_inv_series, &converged_series].into_iter(),
    )?;

    Ok(struct_chunked.into_series())
}
