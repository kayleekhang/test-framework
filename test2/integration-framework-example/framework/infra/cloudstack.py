import json
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from framework.config.models import EnvironmentConfig, ProductConfig


@dataclass
class CloudStackEnvironment:
    env_id: str
    config: EnvironmentConfig
    inventory_path: Path
    config_path: Path
    attached: bool = False

    @classmethod
    def attached_to_config(cls, config_path: Path) -> "CloudStackEnvironment":
        from framework.config.loader import load_environment_config

        config = load_environment_config(config_path)
        return cls(
            env_id=config.env_id,
            config=config,
            inventory_path=config_path.with_suffix(".ini"),
            config_path=config_path,
            attached=True,
        )

    @classmethod
    def create_from_templates(
        cls,
        runtime_dir: Path,
        product_count: int,
        ui_products: set[int],
    ) -> "CloudStackEnvironment":
        env_id = f"it-{uuid4().hex[:8]}"
        products = {}

        for index in range(1, product_count + 1):
            name = f"product{index}"
            has_ui = index in ui_products
            capabilities = ["send_udp", "receive_udp", "send_audio", "receive_audio"]
            if has_ui:
                capabilities.append("web_ui")
            products[name] = ProductConfig(
                name=name,
                ip=f"10.10.0.{index}",
                template="ui-product-template" if has_ui else "service-product-template",
                ui_url=f"https://10.10.0.{index}" if has_ui else None,
                capabilities=tuple(capabilities),
            )

        config = EnvironmentConfig(env_id=env_id, products=products)
        runtime_dir.mkdir(parents=True, exist_ok=True)
        inventory_path = runtime_dir / "inventory.ini"
        config_path = runtime_dir / "environment.json"

        _write_inventory(inventory_path, config)
        _write_config(config_path, config)

        return cls(
            env_id=env_id,
            config=config,
            inventory_path=inventory_path,
            config_path=config_path,
        )

    def destroy(self) -> None:
        """Destroy provisioned VMs in real implementations."""


def _write_inventory(path: Path, config: EnvironmentConfig) -> None:
    lines = ["[products]"]
    for product in config.products.values():
        lines.append(f"{product.name} ansible_host={product.ip} template={product.template}")
    path.write_text("\n".join(lines) + "\n")


def _write_config(path: Path, config: EnvironmentConfig) -> None:
    data = {
        "environment_id": config.env_id,
        "products": {
            name: {
                "ip": product.ip,
                "template": product.template,
                "ui_url": product.ui_url,
                "capabilities": list(product.capabilities),
                "settings": product.settings,
            }
            for name, product in config.products.items()
        },
    }
    path.write_text(json.dumps(data, indent=2) + "\n")
