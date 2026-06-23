from pathlib import Path
import yaml
from framework.common.models import ApplicationConfig, ProductConfig, SystemConfig

class ConfigLoader:
    @staticmethod
    def load_yaml(path: str | Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_system(path: str | Path, target_override: str | None = None) -> SystemConfig:
        raw = ConfigLoader.load_yaml(path)
        system_target = target_override or raw.get("target", "vm")

        products = []
        for product_name, product_raw in raw["products"].items():
            product_target = product_raw.get("target", system_target)

            applications = []
            for app_raw in product_raw.get("applications", []):
                applications.append(ApplicationConfig(
                    name=app_raw["name"],
                    binary_name=app_raw["binary_name"],
                    source_path=app_raw.get("source_path", ""),
                    args=app_raw.get("args", []),
                    builder=app_raw.get("builder", product_raw.get("builder", "stub")),
                    deployer=app_raw.get("deployer", product_raw.get("deployer", "local")),
                    launcher=app_raw.get("launcher", product_raw.get("launcher", "process")),
                    build_profile=app_raw.get("build_profile", "debug"),
                    settings=app_raw.get("settings", {}),
                ))

            products.append(ProductConfig(
                name=product_name,
                product_type=product_raw["product_type"],
                target=product_target,
                applications=applications,
                settings=product_raw.get("settings", {}),
            ))

        return SystemConfig(
            system_name=raw["system_name"],
            system_type=raw["system_type"],
            target=system_target,
            products=products,
            environment=raw.get("environment", "developer"),
        )
