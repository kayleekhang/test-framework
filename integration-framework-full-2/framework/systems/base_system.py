from pathlib import Path
from framework.factory.product_factory import ProductFactory

class BaseSystem:
    def __init__(self, config):
        self.config = config
        self.products = {p.name: ProductFactory.create(p) for p in config.products}

    def build(self, output_dir: Path = Path("artifacts/builds")):
        results = {}
        for name, product in self.products.items():
            results[name] = product.build(output_dir / self.config.system_name / self.config.target)
        return results

    def deploy(self):
        results = {}
        for name, product in self.products.items():
            results[name] = product.deploy()
        return results

    def startup(self):
        for product in self.products.values():
            product.start()
        self.wait_until_healthy()

    def shutdown(self):
        for product in reversed(list(self.products.values())):
            product.stop()

    def wait_until_healthy(self) -> bool:
        for name, product in self.products.items():
            if not product.health_check():
                raise RuntimeError(f"Product not healthy: {name}")
        return True

    def collect_artifacts(self, artifact_dir: Path = Path("artifacts/logs")):
        logs = {}
        for name, product in self.products.items():
            logs[name] = product.collect_logs(artifact_dir / self.config.system_name)
        return logs

    def get_product(self, name: str):
        return self.products[name]
