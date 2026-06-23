from framework.launch.base_launcher import StubLauncher

class SystemdLauncher(StubLauncher):
    name = "systemd"

    def start(self, app):
        print("[SYSTEMD] start " + app.full_name)
        return super().start(app)

    def stop(self, app):
        print("[SYSTEMD] stop " + app.full_name)
        return super().stop(app)
