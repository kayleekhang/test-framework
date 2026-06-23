from dataclasses import dataclass, field
from typing import Any

@dataclass
class ApplicationConfig:
    name: str
    binary_name: str
    source_path: str = ""
    args: list[str] = field(default_factory=list)
    builder: str = "stub"
    deployer: str = "local"
    launcher: str = "process"
    build_profile: str = "debug"
    settings: dict[str, Any] = field(default_factory=dict)

@dataclass
class ProductConfig:
    name: str
    product_type: str
    target: str
    applications: list[ApplicationConfig]
    settings: dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemConfig:
    system_name: str
    system_type: str
    target: str
    products: list[ProductConfig]
    environment: str = "developer"
