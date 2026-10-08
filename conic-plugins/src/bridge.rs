#![allow(clippy::unused_unit)]
use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use serde::Deserialize;

#[derive(Deserialize)]
struct IterationKwargs {
    p_ref: f64,
    max_iter: usize,
    tolerance: f64,
}

fn compute_qtn_output(_input_fields: &[Field]) -> PolarsResult<Field> {
    let fields = vec![
        Field::new("n".into(), DataType::Float64),
        Field::new("qtn".into(), DataType::Float64),
        Field::new("ic".into(), DataType::Float64),
        Field::new("convg".into(), DataType::Boolean),
    ];

    Ok(Field::new("series_output".into(), DataType::Struct(fields)))
}

#[polars_expr(output_type_func=compute_qtn_output)]
fn compute_qtn(inputs: &[Series], kwargs: IterationKwargs) -> PolarsResult<Series> {
    let sv_eff_chunked = inputs[0].f64()?;
    let sv_eff_slice = sv_eff_chunked.cont_slice()?;

    let sv_tot_chunked = inputs[1].f64()?;
    let sv_tot_slice = sv_tot_chunked.cont_slice()?;

    let qt_chunked = inputs[2].f64()?;
    let qt_slice = qt_chunked.cont_slice()?;

    let fr_chunked = inputs[3].f64()?;
    let fr_slice = fr_chunked.cont_slice()?;

    let qtn_vecs = conic_calculate::compute_qtn(
        sv_eff_slice,
        sv_tot_slice,
        qt_slice,
        fr_slice,
        kwargs.p_ref,
        kwargs.max_iter,
        kwargs.tolerance,
    );

    let n_series = Series::new("n".into(), qtn_vecs.n_vec);
    let qtn_series = Series::new("qtn".into(), qtn_vecs.qtn_vec);
    let ic_series = Series::new("ic".into(), qtn_vecs.ic_vec);
    let convg_series = Series::new("convg".into(), qtn_vecs.convg_vec);

    let struct_chunked = StructChunked::from_series(
        "series_output".into(),
        qtn_vecs.vec_size,
        [&n_series, &qtn_series, &ic_series, &convg_series].into_iter(),
    )?;

    Ok(struct_chunked.into_series())
}

fn compute_qc1n_output(_input_fields: &[Field]) -> PolarsResult<Field> {
    let fields = vec![
        Field::new("m".into(), DataType::Float64),
        Field::new("qc1n".into(), DataType::Float64),
        Field::new("qc1ncs".into(), DataType::Float64),
        Field::new("convg".into(), DataType::Boolean),
    ];

    Ok(Field::new("series_output".into(), DataType::Struct(fields)))
}

#[polars_expr(output_type_func=compute_qc1n_output)]
fn compute_qc1n(inputs: &[Series], kwargs: IterationKwargs) -> PolarsResult<Series> {
    let sv_eff_chunked = inputs[0].f64()?;
    let sv_eff_slice = sv_eff_chunked.cont_slice()?;

    let qt_chunked = inputs[1].f64()?;
    let qt_slice = qt_chunked.cont_slice()?;

    let fc_chunked = inputs[2].f64()?;
    let fc_slice = fc_chunked.cont_slice()?;

    let result = conic_correlate::compute_qc1n(
        sv_eff_slice,
        qt_slice,
        fc_slice,
        kwargs.p_ref,
        kwargs.max_iter,
        kwargs.tolerance,
    );

    let m_series = Series::new("m".into(), result.m_vec);
    let qc1n_series = Series::new("qc1n".into(), result.qc1n_vec);
    let qc1ncs_series = Series::new("qc1ncs".into(), result.qc1ncs_vec);
    let convg_series = Series::new("convg".into(), result.convg_vec);

    let struct_chunked = StructChunked::from_series(
        "series_output".into(),
        result.vec_size,
        [&m_series, &qc1n_series, &qc1ncs_series, &convg_series].into_iter(),
    )?;

    Ok(struct_chunked.into_series())
}

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

fn inverse_filter_output(_input_fields: &[Field]) -> PolarsResult<Field> {
    let fields = vec![
        Field::new("qt_inv".into(), DataType::Float64),
        Field::new("fs_inv".into(), DataType::Float64),
        Field::new("converged".into(), DataType::Boolean),
    ];

    Ok(Field::new("series_output".into(), DataType::Struct(fields)))
}

#[polars_expr(output_type_func=inverse_filter_output)]
fn inverse_filter(
    inputs: &[Series],
    kwargs: InverseFilterKwargs,
) -> PolarsResult<Series> {
    let depth_slice = inputs[0].f64()?.cont_slice()?;
    let qt_slice = inputs[1].f64()?.cont_slice()?;
    let fs_slice = inputs[2].f64()?.cont_slice()?;
    let fr_slice = inputs[3].f64()?.cont_slice()?;
    let sv_eff_slice = inputs[4].f64()?.cont_slice()?;
    let sv_tot_slice = inputs[5].f64()?.cont_slice()?;

    let dz = conic_tools::calc_dz(depth_slice)
        .map_err(|msg| polars_err!(ComputeError: "{}", msg))?;

    let params = conic_tools::InverseFilterParams {
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

    let result = conic_tools::inverse_filter(
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
