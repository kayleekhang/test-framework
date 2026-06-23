from framework.deploy.base_deployer import LocalDeployer

class AnsibleDeployer(LocalDeployer):
    name = "ansible"

    def deploy(self, app, artifact):
        result = super().deploy(app, artifact)
        with open(result.artifact, "a", encoding="utf-8") as f:
            f.write("deployer_backend=ansible\n")
        print("[ANSIBLE] deploy " + app.full_name)
        return result
