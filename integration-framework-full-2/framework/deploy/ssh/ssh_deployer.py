from framework.deploy.base_deployer import LocalDeployer

class SSHDeployer(LocalDeployer):
    name = "ssh"

    def deploy(self, app, artifact):
        result = super().deploy(app, artifact)
        with open(result.artifact, "a", encoding="utf-8") as f:
            f.write("deployer_backend=ssh\n")
        print("[SSH] deploy " + app.full_name)
        return result
