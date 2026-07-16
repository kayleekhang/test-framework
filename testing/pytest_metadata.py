from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest


def requirements(*ids: str):
    return _metadata_marker("requirements", *ids)


def capabilities(*ids: str):
    return _metadata_marker("capabilities", *ids)


def products(*names: str):
    return _metadata_marker("products", *names)


def _metadata_marker(marker_name: str, *values: str):
    def decorator(func: Callable[..., Any]):
        return getattr(pytest.mark, marker_name)(*values)(func)

    return decorator


def marker_values(item: pytest.Item, marker_name: str) -> set[str]:
    values: set[str] = set()
    for marker in item.iter_markers(marker_name):
        values.update(str(value) for value in marker.args)
    return values
