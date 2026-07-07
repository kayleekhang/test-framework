from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(frozen=True)
class ProductConfig:
    name: str
    ip: str
    template: str
    capabilities: tuple[str, ...] = ()
    ui_url: Optional[str] = None
    settings: dict[str, Any] = field(default_factory=dict)

    def supports(self, capability: str) -> bool:
        return capability in self.capabilities


@dataclass(frozen=True)
class EnvironmentConfig:
    env_id: str
    products: dict[str, ProductConfig]

    def product(self, name: str) -> ProductConfig:
        return self.products[name]


@dataclass(frozen=True)
class MediaSpec:
    protocol: str
    media_type: str
    count: int = 1
    source_port: int = 5000
    destination_port: int = 5000
