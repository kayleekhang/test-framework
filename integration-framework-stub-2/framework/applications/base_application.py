from pathlib import Path

class BaseApplication:
    def __init__(self, product_name: str, config, product_settings: dict):
        self.product_name = product_name
        self.config = config
        self.product_settings = product_settings
        self.running = False

    @property
    def display_name(self) -> str:
        return f"{self.product_name}.{self.config.name}"

    def build(self, target: str, output_dir: Path):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def health_check(self) -> bool:
        return self.running

    def collect_logs(self, artifact_dir: Path):
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / f"{self.display_name}.log").write_text(
            f"stub log for {self.display_name}\n"
        )
