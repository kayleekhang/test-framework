from pathlib import Path
from framework.applications.base_application import BaseApplication

class SimulatorApplication(BaseApplication):
    def build(self, target: str, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        artifact = output_dir / self.config.binary_name
        artifact.write_text(f"simulator stub for {self.display_name} on {target}\n")
        return artifact

    def start(self):
        print(f"[SIM] start {self.display_name}")
        self.running = True

    def stop(self):
        print(f"[SIM] stop {self.display_name}")
        self.running = False
