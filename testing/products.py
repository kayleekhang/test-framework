from typing import Any

from api import API, APIResponse, Endpoint
from probes import Probe, ProbeFactory
from ui.elements import WebDriver
from ui.pages import Page, PageFactory


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


class ProductFactory:
    PRODUCT_TYPES = {
        "audio_device": AudioDeviceProduct,
        "backend": BackendOnlyProduct,
        "display": DisplayProduct,
    }

    @staticmethod
    def create(driver: WebDriver, config: dict[str, Any]) -> Product:
        api = API(
            endpoints={
                name: Endpoint(**endpoint_config)
                for name, endpoint_config in config.get("api", {}).get("endpoints", {}).items()
            },
            base_headers=config.get("api", {}).get("headers"),
        )

        pages: dict[str, Page] = {}
        ui_config = config.get("ui")

        if ui_config:
            product_prefix = ui_config["selector_prefix"]
            base_url = ui_config["base_url"]
            pages = {
                page_name: PageFactory.create(
                    driver=driver,
                    base_url=base_url,
                    product_prefix=product_prefix,
                    name=page_name,
                    config=page_config,
                )
                for page_name, page_config in ui_config.get("pages", {}).items()
            }

        probes = {
            probe_name: ProbeFactory.create(probe_name, probe_config)
            for probe_name, probe_config in config.get("probes", {}).items()
        }

        product_cls = ProductFactory.PRODUCT_TYPES.get(config.get("product_type"), Product)
        return product_cls(api=api, pages=pages, probes=probes, config=config)
