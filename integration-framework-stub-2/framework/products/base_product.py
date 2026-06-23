from pathlib import Path
from framework.factory.application_factory import ApplicationFactory

class BaseProduct:
    def __init__(self, config):
        self.config = config
        self.apps = [
            ApplicationFactory.create(
                product_name=config.name,
                mode=config.mode,
                app_config=app,
                product_settings=config.settings,
            )
            for app in config.applications
        ]

    @property
    def name(self):
        return self.config.name

    def build(self, output_dir: Path):
        product_dir = output_dir / self.name
        return [app.build(self.config.target, product_dir) for app in self.apps]

    def start(self):
        for app in self.apps:
            app.start()

    def stop(self):
        for app in reversed(self.apps):
            app.stop()

    def health_check(self) -> bool:
        return all(app.health_check() for app in self.apps)

    def collect_logs(self, artifact_dir: Path):
        for app in self.apps:
            app.collect_logs(artifact_dir / self.name)

    def wait_for_state(self, state: str) -> bool:
        print(f"[{self.name}] waiting for state: {state}")
        return self.health_check()
