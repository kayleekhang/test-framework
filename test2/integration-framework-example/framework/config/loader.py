import json
from pathlib import Path

from framework.config.models import EnvironmentConfig, ProductConfig


def load_environment_config(path: Path) -> EnvironmentConfig:
    raw = json.loads(path.read_text())
    products = {
        name: ProductConfig(
            name=name,
            ip=data["ip"],
            template=data["template"],
            ui_url=data.get("ui_url"),
            capabilities=tuple(data.get("capabilities", ())),
            settings=data.get("settings", {}),
        )
        for name, data in raw["products"].items()
    }
    return EnvironmentConfig(env_id=raw["environment_id"], products=products)
