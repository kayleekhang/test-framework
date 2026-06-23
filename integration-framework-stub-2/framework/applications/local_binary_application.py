from pathlib import Path
from framework.applications.base_application import BaseApplication

class LocalBinaryApplication(BaseApplication):
    def build(self, target: str, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        artifact = output_dir / self.config.binary_name
        artifact.write_text(
            f"stub binary: {self.display_name}\n"
            f"target: {target}\n"
            f"profile: {self.config.build_profile}\n"
        )
        return artifact

    def start(self):
        print(f"[LOCAL] start {self.display_name}: {self.config.binary_name} {' '.join(self.config.args)}")
        self.running = True

    def stop(self):
        print(f"[LOCAL] stop {self.display_name}")
        self.running = False
