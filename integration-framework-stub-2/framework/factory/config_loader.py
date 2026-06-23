from pathlib import Path
import yaml
from framework.common.models import ApplicationConfig, ProductConfig, SystemConfig

class ConfigLoader:
    @staticmethod
    def load(path: str | Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_system(path: str | Path, target_override: str | None = None) -> SystemConfig:
        raw = ConfigLoader.load(path)
        target = target_override or raw.get("target", "vm")

        products = []
        for product_name, product_raw in raw["products"].items():
            apps = []
            for app_raw in product_raw.get("applications", []):
                apps.append(ApplicationConfig(
                    name=app_raw["name"],
                    binary_name=app_raw["binary_name"],
                    args=app_raw.get("args", []),
                    build_profile=app_raw.get("build_profile", "debug"),
                ))

            products.append(ProductConfig(
                name=product_name,
                product_type=product_raw["product_type"],
                mode=product_raw.get("mode", "local_binary"),
                target=product_raw.get("target", target),
                applications=apps,
                settings=product_raw.get("settings", {}),
            ))

        return SystemConfig(
            system_name=raw["system_name"],
            system_type=raw["system_type"],
            target=target,
            products=products,
        )
