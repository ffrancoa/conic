# Documentation: frame/filter.rs - replace_rows()

## Overview

The `replace_rows()` function replaces values in rows that contain any indicator
value. When a row has ANY column containing ANY value from the indicators list,
ALL values in that row (except depth) are replaced with `replace_value`.

This is useful for marking invalid measurements while preserving the depth
information for data continuity.

## Function Signature

```rust
pub fn replace_rows(
    data: DataFrame,
    indicators: &[f64],
    replace_value: &f64,
) -> Result<DataFrame, CoreError>
```

**Parameters:**
- `data`: Input DataFrame
- `indicators`: Slice of indicator values to detect (e.g., [-9999.0, -8888.0])
- `replace_value`: Value to use as replacement (commonly f64::NAN)

**Returns:** DataFrame with affected rows replaced

**Common use cases:**
- Replacing invalid measurements with NaN while keeping depth
- Marking problematic data points for visualization
- Preserving row count while invalidating bad data

## How It Works: Step-by-Step

### Example Setup

Input DataFrame:
```
┌─────────┬─────────┬─────────┐
│ Depth   │ qc      │ fs      │
├─────────┼─────────┼─────────┤
│ 1.0     │ 5.0     │ 100.0   │  ← valid row
│ 2.0     │-9999.0  │ 50.0    │  ← indicator in qc
│ 3.0     │ 4.0     │-8888.0  │  ← indicator in fs
│ 4.0     │ 3.0     │ 75.0    │  ← valid row
└─────────┴─────────┴─────────┘
```

Indicators: `[-9999.0, -8888.0]`
Replace value: `f64::NAN`

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

### Step 3: Create per-column checks

```rust
let mask_expr: Vec<Expr> = data
    .get_column_names_str()
    .into_iter()
    .map(|name| col(name).is_in(indicators.clone(), false))
    .collect();
```

For each column, creates a boolean expression checking if values ARE in the
indicators list.

**Note:** Unlike `remove_rows()`, we do NOT use `.not()` here. We want to
identify rows that HAVE indicators.

**Detailed breakdown for column "qc":**

```rust
col("qc").is_in(indicators, false)
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

Final result for "qc": `[false, true, false, false]`

**Similarly for column "fs":**

```
100.0 in [-9999.0, -8888.0]?   → false
50.0 in [-9999.0, -8888.0]?    → false
-8888.0 in [-9999.0, -8888.0]? → true  ✗ (indicator found!)
75.0 in [-9999.0, -8888.0]?    → false
```

Final result for "fs": `[false, false, true, false]`

**Summary of Step 3:**
```rust
mask_expr = [
    [false, true, false, false],   // qc check
    [false, false, true, false],   // fs check
]
```

### Step 4: Combine checks with OR logic

```rust
let mask_expr = any_horizontal(mask_expr)?;
```

`any_horizontal()` combines the per-column checks with OR logic. A row is
marked for replacement if ANY column contains an indicator.

```
Row 0: false OR false → false  (valid - no indicators)
Row 1: true  OR false → true   (indicator in qc - REPLACE!)
Row 2: false OR true  → true   (indicator in fs - REPLACE!)
Row 3: false OR false → false  (valid - no indicators)
```

Result: `[false, true, true, false]` - our global mask

**Key difference from `remove_rows()`:**
- `remove_rows()` uses `all_horizontal()` with AND logic to filter rows
- `replace_rows()` uses `any_horizontal()` with OR logic to mark rows

### Step 5: Create transformation expressions

```rust
let transform_expr: Vec<Expr> = data
    .get_column_names_str()
    .into_iter()
    .map(|name| {
        if name == COL_DEPTH {
            col(name)
        } else {
            when(mask_expr.clone())
                .then(lit(*replace_value))
                .otherwise(col(name))
                .alias(name)
        }
    })
    .collect();
```

For each column, creates an expression that defines what the output column
should contain:

**For the "Depth" column:**
```rust
col("Depth")
```
Simply reference the original column - keep depth unchanged.

**For other columns (e.g., "qc", "fs"):**
```rust
when(mask_expr.clone())
    .then(lit(f64::NAN))
    .otherwise(col("qc"))
    .alias("qc")
```

This is a conditional expression similar to SQL's CASE WHEN:
```sql
CASE
    WHEN mask_expr THEN NaN
    ELSE qc
END AS qc
```

**Breaking down the conditional for "qc":**

`mask_expr` is: `[false, true, true, false]`

```rust
when([false, true, true, false])
    .then(NaN)
    .otherwise(col("qc"))
```

Row-by-row evaluation:
```
Row 0: mask = false → use col("qc") → 5.0     (keep original)
Row 1: mask = true  → use NaN       → NaN     (replace!)
Row 2: mask = true  → use NaN       → NaN     (replace!)
Row 3: mask = false → use col("qc") → 3.0     (keep original)
```

Result for "qc": `[5.0, NaN, NaN, 3.0]`

**Similarly for "fs":**
```
Row 0: mask = false → use col("fs") → 100.0   (keep original)
Row 1: mask = true  → use NaN       → NaN     (replace!)
Row 2: mask = true  → use NaN       → NaN     (replace!)
Row 3: mask = false → use col("fs") → 75.0    (keep original)
```

Result for "fs": `[100.0, NaN, NaN, 75.0]`

**The `.alias(name)` part:**
Ensures the output column has the same name as the input column. Without this,
Polars might generate a default name.

**Summary of Step 5:**
```rust
transform_expr = [
    col("Depth"),                                    // keep as-is
    when(mask).then(NaN).otherwise(col("qc")).alias("qc"),
    when(mask).then(NaN).otherwise(col("fs")).alias("fs"),
]
```

### Step 6: Apply transformations

```rust
let out_data = data
    .lazy()
    .select(transform_expr)
    .collect()?;
```

`.select()` creates a new DataFrame where each column is defined by the
corresponding expression from `transform_expr`.

**What `.select()` does:**
Despite its name, `.select()` doesn't just "select" existing columns - it can
also transform them. It accepts `Expr` (expressions), which can be:
- Simple references: `col("Depth")` - copy column as-is
- Transformations: `when(...).then(...).otherwise(...)` - conditional logic

This is similar to SQL's `SELECT` clause:
```sql
SELECT
    Depth,
    CASE WHEN mask THEN NaN ELSE qc END AS qc,
    CASE WHEN mask THEN NaN ELSE fs END AS fs
FROM data
```

**Final output:**
```
┌─────────┬─────────┬─────────┐
│ Depth   │ qc      │ fs      │
├─────────┼─────────┼─────────┤
│ 1.0     │ 5.0     │ 100.0   │
│ 2.0     │ NaN     │ NaN     │  ← replaced (had indicator in qc)
│ 3.0     │ NaN     │ NaN     │  ← replaced (had indicator in fs)
│ 4.0     │ 3.0     │ 75.0    │
└─────────┴─────────┴─────────┘
```

Notice that Row 1 has ALL values replaced (even though indicator was only in
qc), and Row 2 has ALL values replaced (even though indicator was only in fs).
Only depth is preserved.

## Key Concepts

### Why OR logic instead of AND?

For replacement, we want to mark an ENTIRE row as invalid if ANY column has an
indicator. Using `any_horizontal()` with OR logic achieves this:
- Row with indicator in qc only → entire row replaced
- Row with indicator in fs only → entire row replaced
- Row with indicators in multiple columns → entire row replaced

### Why preserve depth?

Depth is typically the index/position information for CPTu data. Preserving it
maintains:
1. Data continuity (same number of rows)
2. Spatial reference (know where invalid data occurred)
3. Ability to plot data with gaps visible

### Why use `.select()` instead of `.with_columns()`?

Both could work, but `.select()` is more explicit here:
- `.select()`: "Create these exact columns" (clear intent to transform all)
- `.with_columns()`: "Add/update these columns" (implies keeping others)

Since we're transforming ALL columns (either keep or replace), `.select()`
better expresses the operation.

### Why clone `mask_expr` in the map?

The `.map()` iterator needs to use `mask_expr` for each column. Since `Expr`
doesn't implement `Copy`, we clone it. This is cheap - it only clones the
expression description, not the actual data.

### When would you use NaN vs a sentinel value?

- **NaN (f64::NAN)**: Recommended for mathematical operations. NaN propagates
  through calculations (e.g., `NaN + 5.0 = NaN`), preventing invalid data from
  contaminating results.

- **Sentinel value (e.g., -9999.0)**: Only use if external systems require it.
  Risk: might accidentally be used in calculations.

## Performance Notes

- For files < 1000 rows (typical CPTu data), performance is excellent
- `any_horizontal()` is optimized for row-wise OR operations
- Lazy evaluation minimizes memory overhead
- `.select()` with expressions allows Polars to optimize the query plan
