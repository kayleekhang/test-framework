from pathlib import Path
from typing import Any


def load_product_config(config_path: str | Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        yaml = None

    with Path(config_path).open("r", encoding="utf-8") as config_file:
        if yaml is not None:
            config = yaml.safe_load(config_file)
        else:
            config = _load_simple_yaml_mapping(config_file.read())

    if not isinstance(config, dict):
        raise ValueError(f"Product config must be a YAML mapping: {config_path}")

    return config


def _load_simple_yaml_mapping(yaml_text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for line_number, raw_line in enumerate(yaml_text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        key, separator, raw_value = line.partition(":")

        if not separator:
            raise ValueError(f"Unsupported YAML line {line_number}: {raw_line}")

        while indent <= stack[-1][0]:
            stack.pop()

        parent = stack[-1][1]
        value = raw_value.strip()

        if value:
            parent[key] = _parse_simple_yaml_scalar(value)
            continue

        child: dict[str, Any] = {}
        parent[key] = child
        stack.append((indent, child))

    return root


def _parse_simple_yaml_scalar(value: str) -> Any:
    if value == "{}":
        return {}

    if value in {"true", "false"}:
        return value == "true"

    if value in {"null", "None"}:
        return None

    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return value[1:-1]

    try:
        return int(value)
    except ValueError:
        return value
