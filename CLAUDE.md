# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**conic** is a CPTu (Cone Penetration Test with pore pressure measurement) data processing tool designed as a library-first architecture with a CLI wrapper. The project aims to support both command-line usage and Python API integration.

## Build Commands

```bash
# Build entire workspace
cargo build

# Build only the core library
cargo build -p conic-core

# Build only the CLI
cargo build -p conic-cli

# Run the CLI (currently hardcoded demo)
cargo run -p conic-cli

# Run with release optimizations
cargo run -p conic-cli --release

# Build release binaries
cargo build --release
```

## Testing & Benchmarking

```bash
# Run all tests (currently none implemented)
cargo test

# Run tests for specific crate
cargo test -p conic-core

# Run benchmarks (skeleton exists in conic-core/benches/conic_bench.rs, not implemented)
cargo bench -p conic-core
```

## Code Quality

```bash
# Check code without building
cargo check

# Run clippy linter
cargo clippy

# Format code
cargo fmt

# Check formatting without modifying
cargo fmt -- --check
```

## Code Style

### Comment Guidelines

**All comments must be in English.**

- **Documentation comments (`///`)**: Start with uppercase letter
  ```rust
  /// Computes basic stress-related parameters from CPTu data.
  pub fn basic_params(data: DataFrame) -> Result<DataFrame, CoreError> {
  ```

- **Inline comments (`//`)**: Start with lowercase letter
  ```rust
  // total vertical stress = γ * z
  let sigma_v = gamma * depth;
  ```

## Architecture

### Workspace Structure

This is a Cargo workspace with two crates:

- **conic-core**: Core library containing all CPTu calculation logic, I/O, and error handling
- **conic-cli**: Thin CLI wrapper (currently just a hardcoded demo in main.rs)

The separation enables `conic-core` to be reused as a library (e.g., for Python bindings via PyO3/maturin).

### Core Library Organization (`conic-core/src/`)

```
conic-core/src/
├── lib.rs           # Public API surface (re-exports io, calc, error modules)
├── error.rs         # CoreError type with thiserror integration
├── io.rs            # CSV reading with schema validation
└── calc/
    ├── mod.rs       # Module declarations
    ├── clean.rs     # Data filtering (removes error indicators)
    └── compute.rs   # CPT parameter calculations
```

### Data Processing Pipeline

The typical workflow implemented in `conic-cli/src/main.rs`:

1. **Read CSV** (`io::read_csv`) → Validates required columns: "Depth (m)", "qc (MPa)", "fs (kPa)", "u2 (kPa)"
2. **Clean Data** (`calc::clean::filter_rows`) → Removes rows with error indicators (-9999, -8888, -7777)
3. **Basic Parameters** (`calc::compute::basic_params`) → Computes:
   - σv_tot: Total vertical stress
   - σv_eff: Effective vertical stress
   - qt: Corrected cone resistance
   - Fr: Normalized friction ratio
   - Bq: Pore pressure ratio
4. **Derived Parameters** (`calc::compute::derived_params`) → Iterative calculation of:
   - n: Stress exponent
   - Qtn: Normalized tip resistance
   - Ic: Soil behavior type index (using iterative convergence)

### CPTu Calculations

The `compute.rs` module implements geotechnical formulations:

- **basic_params**: Uses Polars lazy evaluation for efficient transformations. Requires `area_ratio` (cone area ratio, typically 0.8) and `gamma_soil` (soil unit weight in kN/m³).

- **derived_params**: Implements iterative algorithm to calculate soil behavior type index (Ic):
  - Converges stress exponent `n` using fixed-point iteration
  - Max 999 iterations with tolerance 1e-3
  - Handles negative Fr values (skips calculation, sets NaN)
  - Returns convergence status for each row

### Error Handling

Uses `thiserror` for structured error types:
- `CoreError::Io`: File system errors
- `CoreError::Polars`: DataFrame operation errors
- `CoreError::InvalidData`: Schema validation failures

All public functions return `Result<T, CoreError>`.

### Dependencies

- **polars 0.52.0**: DataFrame operations with lazy evaluation (features: "is_in", "lazy", "timezones")
  - Note: The "timezones" feature is required in 0.52.0 to avoid compilation errors in `polars-expr`
- **thiserror 2.0.17**: Error handling macros
- **criterion 0.8.0** (dev): Benchmarking framework (not yet used)

## Current State & Incomplete Features

### Implemented ✓
- Core library with CPTu calculations
- CSV I/O with validation
- Data cleaning pipeline
- Basic and derived parameter computations
- Proper error handling

### Not Implemented ✗
- Functional CLI (main.rs is hardcoded demo)
- Command-line argument parsing
- Python API bindings
- Unit tests
- Benchmarks (stub exists)
- Documentation (rustdoc)
- Multiple dataset handling
- Output to file functionality

## Test Data

Test CSV files in `test/` directory:
- Required columns: "Depth (m)", "qc (MPa)", "fs (kPa)", "u2 (kPa)", "u0 (kPa)"
- Error indicators: -9999, -8888, -7777 (must be filtered before computation)

## Development Notes

- **Rust Edition**: 2024 (requires recent Rust toolchain)
- **License**: MPL-2.0
- **Polars Usage**: Leverage lazy evaluation (`LazyFrame`) for performance
- **Type Coercion**: All columns cast to Float64 during I/O
- **Future Direction**: CLI needs implementation with proper command parsing; Python bindings are planned but not started
