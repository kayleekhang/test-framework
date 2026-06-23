from pathlib import Path
from framework.applications.base_application import BaseApplication

class RemoteBinaryApplication(BaseApplication):
    def build(self, target: str, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        artifact = output_dir / self.config.binary_name
        artifact.write_text(f"remote deployable stub for {self.display_name} on {target}\n")
        return artifact

    def start(self):
        host = self.product_settings.get("host", "unknown-host")
        user = self.product_settings.get("ssh_user", "test")
        print(f"[SSH] {user}@{host} start {self.display_name}")
        self.running = True

    def stop(self):
        host = self.product_settings.get("host", "unknown-host")
        print(f"[SSH] {host} stop {self.display_name}")
        self.running = False
