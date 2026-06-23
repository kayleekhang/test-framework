from pathlib import Path
from framework.factory.builder_factory import BuilderFactory
from framework.factory.deployer_factory import DeployerFactory
from framework.factory.launcher_factory import LauncherFactory

class Application:
    def __init__(self, product_name: str, target: str, product_settings: dict, config):
        self.product_name = product_name
        self.target = target
        self.product_settings = product_settings
        self.config = config
        self.running = False
        self.last_build_artifact: Path | None = None
        self.last_deploy_artifact: Path | None = None

        self.builder = BuilderFactory.create(config.builder)
        self.deployer = DeployerFactory.create(config.deployer)
        self.launcher = LauncherFactory.create(config.launcher)

    @property
    def full_name(self) -> str:
        return f"{self.product_name}.{self.config.name}"

    def build(self, output_dir: Path):
        result = self.builder.build(self, output_dir)
        self.last_build_artifact = result.artifact
        return result

    def deploy(self):
        if self.last_build_artifact is None:
            raise RuntimeError(f"{self.full_name} must be built before deploy")
        result = self.deployer.deploy(self, self.last_build_artifact)
        self.last_deploy_artifact = result.artifact
        return result

    def start(self):
        return self.launcher.start(self)

    def stop(self):
        return self.launcher.stop(self)

    def health_check(self) -> bool:
        return self.launcher.health_check(self)

    def collect_logs(self, artifact_dir: Path):
        artifact_dir.mkdir(parents=True, exist_ok=True)
        log = artifact_dir / f"{self.full_name}.log"
        log.write_text(
            f"log for {self.full_name}\n"
            f"target={self.target}\n"
            f"running={self.running}\n"
        )
        return log
