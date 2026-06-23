from framework.common.result import OperationResult

class BaseLauncher:
    name = "base"

    def start(self, app) -> OperationResult:
        raise NotImplementedError

    def stop(self, app) -> OperationResult:
        raise NotImplementedError

    def health_check(self, app) -> bool:
        return app.running

class StubLauncher(BaseLauncher):
    name = "stub"

    def start(self, app) -> OperationResult:
        app.running = True
        print(f"[LAUNCH] start {app.full_name}")
        return OperationResult(True, app.full_name, "started")

    def stop(self, app) -> OperationResult:
        app.running = False
        print(f"[LAUNCH] stop {app.full_name}")
        return OperationResult(True, app.full_name, "stopped")
