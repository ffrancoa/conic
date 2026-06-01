use pyo3_polars::PolarsAllocator;

mod _calc;
mod _impl;

#[global_allocator]
static ALLOC: PolarsAllocator = PolarsAllocator::new();
