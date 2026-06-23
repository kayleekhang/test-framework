from framework.deploy.base_deployer import LocalDeployer

class DockerDeployer(LocalDeployer):
    name = "docker"

    def deploy(self, app, artifact):
        result = super().deploy(app, artifact)
        with open(result.artifact, "a", encoding="utf-8") as f:
            f.write("deployer_backend=docker\n")
        print("[DOCKER] deploy " + app.full_name)
        return result
