use std::hint::black_box;

use criterion::{criterion_group, criterion_main, Criterion};

use conic_core::{calc, io};

fn bench_clean_nan(c: &mut Criterion) {
    let df = io::read_csv("../test/sh23-104.csv").unwrap();
    let nan_indicators = vec![-9999.0, -8888.0, -7777.0];

    c.bench_function("clean_nan_values", |b| {
        b.iter(|| {
            let _ = calc::clean_nan_values(black_box(df.clone()), black_box(nan_indicators.clone()));
        })
    });

    c.bench_function("drop_value_rows", |b| {
        b.iter(|| {
            let _ = calc::drop_value_rows(black_box(df.clone()), black_box(nan_indicators.clone()));
        })
    });
}

criterion_group!(benches, bench_clean_nan);
criterion_main!(benches);