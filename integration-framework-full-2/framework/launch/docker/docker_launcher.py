from framework.launch.base_launcher import StubLauncher

class DockerLauncher(StubLauncher):
    name = "docker"

    def start(self, app):
        print("[DOCKER] start " + app.full_name)
        return super().start(app)

    def stop(self, app):
        print("[DOCKER] stop " + app.full_name)
        return super().stop(app)
