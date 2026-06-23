from dataclasses import dataclass
from typing import Any

@dataclass
class ApplicationConfig:
    name: str
    binary_name: str
    args: list[str]
    build_profile: str = "debug"

@dataclass
class ProductConfig:
    name: str
    product_type: str
    mode: str
    target: str
    applications: list[ApplicationConfig]
    settings: dict[str, Any]

@dataclass
class SystemConfig:
    system_name: str
    system_type: str
    target: str
    products: list[ProductConfig]
