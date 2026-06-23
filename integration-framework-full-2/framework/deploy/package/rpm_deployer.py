from framework.deploy.base_deployer import LocalDeployer

class RpmDeployer(LocalDeployer):
    name = "rpm"

    def deploy(self, app, artifact):
        result = super().deploy(app, artifact)
        with open(result.artifact, "a", encoding="utf-8") as f:
            f.write("deployer_backend=rpm\n")
        print("[RPM] deploy " + app.full_name)
        return result
