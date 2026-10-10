from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from conic.workflow import catalog as catalog


def __getattr__(name: str) -> object:
    if name == "catalog":
        from conic.workflow import catalog

        return catalog

    raise AttributeError(f"module 'conic' has no attribute {name!r}")
