use pyo3_polars::PolarsAllocator;

mod conic;


#[global_allocator]
static ALLOC: PolarsAllocator = PolarsAllocator::new();
