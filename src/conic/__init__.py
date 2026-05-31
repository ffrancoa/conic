from pathlib import Path

import polars as pl

from polars.plugins import register_plugin_function

from conic._typing import IntoExprColumn

LIB_PATH = Path(__file__).parent


def abs_numeric(expr: IntoExprColumn) -> pl.Expr:
    return register_plugin_function(
        plugin_path=LIB_PATH,
        args=[expr],
        function_name="abs_numeric",
        is_elementwise=True,
    )


def main() -> None:
    df = pl.DataFrame(
        {"a": [1, -1, None], "b": [4.1, 5.2, -6.3], "c": ["hello", "everybody!", "!"]}
    )

    result = df.with_columns(abs_numeric(pl.col("a", "b").name.suffix("_abs")))
    print(result)


if __name__ == "__main__":
    main()
