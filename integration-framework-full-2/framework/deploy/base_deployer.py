from pathlib import Path
from framework.common.result import OperationResult

class BaseDeployer:
    name = "base"

    def deploy(self, app, artifact: Path) -> OperationResult:
        raise NotImplementedError

class LocalDeployer(BaseDeployer):
    name = "local"

    def deploy(self, app, artifact: Path) -> OperationResult:
        deploy_dir = Path("artifacts/deployments") / app.product_name
        deploy_dir.mkdir(parents=True, exist_ok=True)
        deployed = deploy_dir / artifact.name
        deployed.write_text(artifact.read_text())
        return OperationResult(True, app.full_name, "deployed locally", deployed)
