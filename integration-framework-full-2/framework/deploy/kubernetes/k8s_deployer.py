from framework.deploy.base_deployer import LocalDeployer

class K8sDeployer(LocalDeployer):
    name = "kubernetes"

    def deploy(self, app, artifact):
        result = super().deploy(app, artifact)
        with open(result.artifact, "a", encoding="utf-8") as f:
            f.write("deployer_backend=kubernetes\n")
        print("[K8S] deploy " + app.full_name)
        return result
