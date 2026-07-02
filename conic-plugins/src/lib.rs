use pyo3_polars::PolarsAllocator;

mod bridge;

#[global_allocator]
static ALLOC: PolarsAllocator = PolarsAllocator::new();
