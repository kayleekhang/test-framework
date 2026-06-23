from pathlib import Path
from framework.applications.base_application import BaseApplication

class SystemdApplication(BaseApplication):
    def build(self, target: str, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        artifact = output_dir / self.config.binary_name
        artifact.write_text(f"systemd service binary stub for {self.display_name} on {target}\n")
        return artifact

    def start(self):
        service_name = self.product_settings.get("service_name", f"{self.config.name}.service")
        host = self.product_settings.get("host", "localhost")
        print(f"[SYSTEMD] {host}: sudo systemctl start {service_name}")
        self.running = True

    def stop(self):
        service_name = self.product_settings.get("service_name", f"{self.config.name}.service")
        host = self.product_settings.get("host", "localhost")
        print(f"[SYSTEMD] {host}: sudo systemctl stop {service_name}")
        self.running = False
