from framework.launch.base_launcher import StubLauncher

class PodLauncher(StubLauncher):
    name = "kubernetes"

    def start(self, app):
        print("[K8S] start " + app.full_name)
        return super().start(app)

    def stop(self, app):
        print("[K8S] stop " + app.full_name)
        return super().stop(app)
