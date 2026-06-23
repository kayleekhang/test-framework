from pathlib import Path

class BaseSystem:
    def __init__(self, config, products: dict):
        self.config = config
        self.products = products

    def build(self, output_dir: Path):
        artifacts = {}
        for name, product in self.products.items():
            artifacts[name] = product.build(output_dir)
        return artifacts

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
                raise RuntimeError(f"Product is not healthy: {name}")
        return True

    def collect_artifacts(self, artifact_dir: Path = Path("artifacts")):
        for product in self.products.values():
            product.collect_logs(artifact_dir)
