use std::hint::black_box;

use criterion::{criterion_group, criterion_main, Criterion};

use conic_core::{calc, io};

fn bench_clean_nan(c: &mut Criterion) {
    let df = io::read_csv("../test/sh23-102.csv").unwrap();
    let nan_indicators = vec![-9999.0, -8888.0, -7777.0];

    // finished: ~1.0178 ms
    c.bench_function("clean_nan_values", |b| {
        b.iter(|| {
            let _ = calc::clean_nan_values(black_box(df.clone()), black_box(nan_indicators.clone()));
        })
    });

    // finished: ~373.46 µs
    c.bench_function("drop_value_rows", |b| {
        b.iter(|| {
            let _ = calc::drop_value_rows(black_box(df.clone()), black_box(nan_indicators.clone()));
        })
    });
}

criterion_group!(benches, bench_clean_nan);
criterion_main!(benches);