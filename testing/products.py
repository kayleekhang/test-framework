from typing import Any

from api import API, APIResponse
from probes import Probe
from ui.pages import Page


class Product:
    def __init__(
        self,
        api: API,
        pages: dict[str, Page],
        probes: dict[str, Probe],
        config: dict[str, Any],
    ):
        self.api = api
        self.pages = pages
        self.probes = probes
        self.config = config

    @property
    def has_ui(self) -> bool:
        return bool(self.pages)

    def page(self, name: str) -> Page:
        if name not in self.pages:
            available = ", ".join(sorted(self.pages)) or "none"
            raise KeyError(f"Unknown page '{name}'. Available pages: {available}")
        return self.pages[name]

    def probe(self, name: str) -> Probe:
        if name not in self.probes:
            available = ", ".join(sorted(self.probes)) or "none"
            raise KeyError(f"Unknown probe '{name}'. Available probes: {available}")
        return self.probes[name]


class BackendOnlyProduct(Product):
    pass


class DisplayProduct(Product):
    def health(self) -> APIResponse:
        return self.api.request("health")


class AudioDeviceProduct(BackendOnlyProduct):
    def send_test_tone(self):
        return self.probe("send_test_tone").run_pipeline()

    def receive_audio(self):
        return self.probe("receive_audio").run_pipeline()

    def capture_audio_packets(self, timeout_seconds: int | None = None):
        return self.probe("audio_packets").capture(timeout_seconds=timeout_seconds)
