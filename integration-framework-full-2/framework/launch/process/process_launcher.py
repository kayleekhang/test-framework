from framework.launch.base_launcher import StubLauncher

class ProcessLauncher(StubLauncher):
    name = "process"

    def start(self, app):
        print("[PROCESS] start " + app.full_name)
        return super().start(app)

    def stop(self, app):
        print("[PROCESS] stop " + app.full_name)
        return super().stop(app)
