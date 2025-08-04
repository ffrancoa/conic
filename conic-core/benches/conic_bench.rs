use criterion::{criterion_group, criterion_main, Criterion};

fn conic_bench(_c: &mut Criterion) {
    todo!();
}

criterion_group!(benches, conic_bench);
criterion_main!(benches);