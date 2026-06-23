from framework.deploy.base_deployer import LocalDeployer

class SCPDeployer(LocalDeployer):
    name = "scp"

    def deploy(self, app, artifact):
        result = super().deploy(app, artifact)
        with open(result.artifact, "a", encoding="utf-8") as f:
            f.write("deployer_backend=scp\n")
        print("[SCP] deploy " + app.full_name)
        return result
