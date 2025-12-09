# Documentation: frame/filter.rs - remove_rows()

## Overview

The `remove_rows()` function removes rows from a DataFrame that contain any
of the specified indicator values. A row is eliminated if ANY column contains
ANY value from the indicators list.

## Function Signature

```rust
pub fn remove_rows(
    data: DataFrame,
    indicators: &[f64],
) -> Result<DataFrame, CoreError>
```

**Parameters:**
- `data`: Input DataFrame
- `indicators`: Slice of indicator values to remove (e.g., [-9999.0, -8888.0])

**Returns:** DataFrame with rows removed

**Common use cases:**
- Removing error indicators from CPTu data
- Excluding sentinel values
- Filtering out invalid measurements

## How It Works: Step-by-Step

### Example Setup

Input DataFrame:
```
┌─────────┬─────────┐
│ qc      │ fs      │
├─────────┼─────────┤
│ 5.0     │ 100.0   │  ← valid row
│-9999.0  │ 50.0    │  ← indicator in qc
│ 4.0     │-8888.0  │  ← indicator in fs
│ 3.0     │ 75.0    │  ← valid row
└─────────┴─────────┘
```

Indicators: `[-9999.0, -8888.0]`

### Step 1: Create indicator series

```rust
let indicators = Series::from_vec(
    "indicators".into(),
    indicators.to_vec(),
);
// Series: [-9999.0, -8888.0]
```

Converts the input slice into a Polars Series.

### Step 2: Convert to lazy expression

```rust
let indicators = lit(indicators).implode();
// Expr representing: [[-9999.0, -8888.0]]
```

**What is `.implode()`?**
Converts scalar values into a list. Required because `is_in()` expects a list
for membership checking.

**What is `Expr`?**
`Expr` is Polars' type for lazy expressions - operations that describe what to
do but don't execute immediately. They only run when `.collect()` is called.

### Step 3: Create per-column checks

```rust
let mask_expr: Vec<Expr> = data
    .get_column_names_str()
    .into_iter()
    .map(|name| col(name).is_in(indicators.clone(), false).not())
    .collect();
```

For each column, creates a boolean expression checking if values are NOT in
the indicators list.

**Detailed breakdown for column "qc":**

```rust
col("qc").is_in(indicators, false).not()
```

**Sub-step A:** `col("qc")`
Reference to column qc: `[5.0, -9999.0, 4.0, 3.0]`

**Sub-step B:** `.is_in(indicators, false)`
For each value, asks: "Is this value in the indicators list?"

```
5.0 in [-9999.0, -8888.0]?      → false
-9999.0 in [-9999.0, -8888.0]?  → true  ✗ (indicator found!)
4.0 in [-9999.0, -8888.0]?      → false
3.0 in [-9999.0, -8888.0]?      → false
```

Result: `[false, true, false, false]`

**Sub-step C:** `.not()`
Inverts booleans (we want to KEEP rows WITHOUT indicators)

```
not(false) → true  ✓
not(true)  → false ✗
not(false) → true  ✓
not(false) → true  ✓
```

Final result for "qc": `[true, false, true, true]`

**Similarly for column "fs":**

```
100.0 in [-9999.0, -8888.0]?   → false → not(false) → true ✓
50.0 in [-9999.0, -8888.0]?    → false → not(false) → true ✓
-8888.0 in [-9999.0, -8888.0]? → true  → not(true)  → false ✗
75.0 in [-9999.0, -8888.0]?    → false → not(false) → true ✓
```

Final result for "fs": `[true, true, false, true]`

**Summary of Step 3:**
```rust
mask_expr = [
    [true, false, true, true],   // qc check
    [true, true, false, true],   // fs check
]
```

### Step 4: Combine checks with AND logic

```rust
let mask_expr = all_horizontal(mask_expr)?;

let out_data = data
    .lazy()
    .filter(mask_expr)
    .collect()?;
```

`all_horizontal()` combines the per-column checks with AND logic:

```
Row 0: true  AND true  → true  ✓ KEEP
Row 1: false AND true  → false ✗ REMOVE (indicator in qc)
Row 2: true  AND false → false ✗ REMOVE (indicator in fs)
Row 3: true  AND true  → true  ✓ KEEP
```

**Final output:**
```
┌─────────┬─────────┐
│ qc      │ fs      │
├─────────┼─────────┤
│ 5.0     │ 100.0   │
│ 3.0     │ 75.0    │
└─────────┴─────────┘
```

## Key Concepts

### Why `is_in()` and not the reverse?

Polars API design: `col(name).is_in(list)` asks "Is the column value in the
list?", similar to Python's `value in list` operator.

There is no inverse method like `list.contains(col(name))` in Polars.

### Why clone `indicators`?

The `.map()` iterator needs to use `indicators` for each column. Since `Expr`
doesn't implement `Copy`, we clone it. This is cheap - it only clones the
expression description, not the actual data.

### Why lazy evaluation?

Lazy evaluation (.lazy() and Expr) allows Polars to:
1. Optimize the query plan before execution
2. Potentially parallelize operations
3. Minimize memory usage by avoiding intermediate DataFrames

The actual computation happens only when `.collect()` is called.

## Performance Notes

- For files < 1000 rows (typical CPTu data), performance is excellent
- `all_horizontal()` is optimized for row-wise AND operations
- Lazy evaluation minimizes memory overhead
