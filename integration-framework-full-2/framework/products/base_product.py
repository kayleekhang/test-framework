from pathlib import Path
from framework.factory.application_factory import ApplicationFactory

class BaseProduct:
    def __init__(self, config):
        self.config = config
        self.apps = [
            ApplicationFactory.create(
                product_name=config.name,
                product_target=config.target,
                product_settings=config.settings,
                app_config=app_config,
            )
            for app_config in config.applications
        ]

    @property
    def name(self):
        return self.config.name

    def build(self, output_dir: Path):
        product_dir = output_dir / self.name
        return [app.build(product_dir) for app in self.apps]

    def deploy(self):
        return [app.deploy() for app in self.apps]

    def start(self):
        return [app.start() for app in self.apps]

    def stop(self):
        return [app.stop() for app in reversed(self.apps)]

    def health_check(self) -> bool:
        return all(app.health_check() for app in self.apps)

    def wait_for_state(self, state: str) -> bool:
        print(f"[{self.name}] wait_for_state({state})")
        return self.health_check()

    def collect_logs(self, artifact_dir: Path):
        logs = []
        for app in self.apps:
            logs.append(app.collect_logs(artifact_dir / self.name))
        return logs
