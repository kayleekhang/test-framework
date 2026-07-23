from __future__ import annotations

from copy import deepcopy
from typing import Any

from api import API, APIResponse, Endpoint
from probes import Probe, ProbeFactory
from ui.elements import WebDriver
from ui.pages import Page, PageFactory
from ui.selenium import SeleniumWrapper
from websockets_client import WebSocketChannel, WebSocketFactory


class Product:
    def __init__(
        self,
        api: API,
        pages: dict[str, Page],
        probes: dict[str, Probe],
        websockets: dict[str, WebSocketChannel],
        capability_config: dict[str, Any],
        operational_config: dict[str, Any],
        name: str | None = None,
        ip: str | None = None,
        selenium: SeleniumWrapper | None = None,
    ):
        self.api = api
        self.pages = pages
        self.probes = probes
        self.websockets = websockets
        self.capability_config = capability_config
        self.operational_config = operational_config
        # Backwards-compatible alias for callers that used product.config.
        self.config = capability_config
        self.name = name
        self.ip = ip
        self.selenium = selenium
        self.current_page: Page | None = None

    @property
    def has_ui(self) -> bool:
        return bool(self.pages)

    def page(self, name: str) -> Page:
        if name not in self.pages:
            available = ", ".join(sorted(self.pages)) or "none"
            raise KeyError(f"Unknown page '{name}'. Available pages: {available}")
        return self.pages[name]

    def open(self, page_name: str) -> Product:
        self.current_page = self.page(page_name).open()
        return self

    def click(self, element_name: str) -> Product:
        self._current_page().click(element_name)
        return self

    def text(self, element_name: str) -> str:
        return self._current_page().text(element_name)

    def is_visible(self, element_name: str) -> bool:
        return self._current_page().is_visible(element_name)

    def websocket(self, name: str) -> WebSocketChannel:
        if name not in self.websockets:
            available = ", ".join(sorted(self.websockets)) or "none"
            raise KeyError(f"Unknown WebSocket '{name}'. Available channels: {available}")
        return self.websockets[name]

    def quit(self) -> None:
        if self.selenium is not None:
            self.selenium.quit()

    def _current_page(self) -> Page:
        if self.current_page is None:
            raise RuntimeError("Open a page before interacting with its elements.")
        return self.current_page

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
    def create(
        driver: WebDriver = None,
        config: dict[str, Any] | None = None,
        *,
        capability_config: dict[str, Any] | None = None,
        operational_config: dict[str, Any] | None = None,
        product_group: str | None = None,
        product_name: str | None = None,
    ) -> Product:
        capability = deepcopy(capability_config or config or {})
        operation = ProductFactory._select_operation(
            operational_config=operational_config,
            product_group=product_group,
            product_name=product_name,
        )
        host = operation.get("ip") or operation.get("host")

        api_config = capability.get("api", {})
        endpoints = {}
        for name, endpoint_config in api_config.get("endpoints", {}).items():
            resolved = deepcopy(endpoint_config)
            if host:
                resolved["host"] = host
            elif "host" not in resolved:
                raise ValueError(f"API endpoint '{name}' needs an operational IP or host")
            endpoints[name] = Endpoint(**resolved)
        api = API(endpoints=endpoints, base_headers=api_config.get("headers"))

        pages: dict[str, Page] = {}
        selenium = None
        ui_config = capability.get("ui")
        if ui_config:
            base_url = ProductFactory._ui_base_url(ui_config, operation)
            selenium = SeleniumWrapper(
                base_url=base_url,
                config=ui_config.get("selenium"),
                driver=driver,
            )
            pages = {
                page_name: PageFactory.create(
                    driver=selenium,
                    base_url=base_url,
                    product_prefix=ui_config.get("selector_prefix", ""),
                    selector_suffix=operation.get("name", ""),
                    name=page_name,
                    config=page_config,
                )
                for page_name, page_config in ui_config.get("pages", {}).items()
            }

        probes = {
            name: ProbeFactory.create(name, probe_config)
            for name, probe_config in capability.get("probes", {}).items()
        }
        websockets = {
            name: WebSocketFactory.create(name, channel_config, host=host)
            for name, channel_config in capability.get("websockets", {}).items()
        }

        product_cls = ProductFactory.PRODUCT_TYPES.get(
            capability.get("product_type"), Product
        )
        return product_cls(
            api=api,
            pages=pages,
            probes=probes,
            websockets=websockets,
            capability_config=capability,
            operational_config=operation,
            name=operation.get("name"),
            ip=host,
            selenium=selenium,
        )

    @staticmethod
    def _ui_base_url(ui_config: dict[str, Any], operation: dict[str, Any]) -> str:
        host = operation.get("ip") or operation.get("host")
        if not host:
            if "base_url" in ui_config:
                return ui_config["base_url"].rstrip("/")
            raise ValueError("UI capability needs an operational IP or host")

        protocol = operation.get("ui_protocol", ui_config.get("protocol", "https"))
        port = operation.get("ui_port", ui_config.get("port", 8080))
        return f"{protocol}://{host}:{port}"

    @staticmethod
    def _select_operation(
        operational_config: dict[str, Any] | None,
        product_group: str | None,
        product_name: str | None,
    ) -> dict[str, Any]:
        if operational_config is None:
            if product_name or product_group:
                raise ValueError(
                    "product_group and product_name require operational_config"
                )
            return {}

        if not product_group or not product_name:
            raise ValueError(
                "product_group and product_name are required with operational_config"
            )
        if product_group not in operational_config:
            available = ", ".join(sorted(operational_config)) or "none"
            raise KeyError(
                f"Unknown operational product group '{product_group}'. "
                f"Available groups: {available}"
            )

        matches = [
            instance
            for instance in operational_config[product_group]
            if instance.get("name") == product_name
        ]
        if not matches:
            available = ", ".join(
                instance.get("name", "<unnamed>")
                for instance in operational_config[product_group]
            ) or "none"
            raise KeyError(
                f"Unknown product '{product_name}' in '{product_group}'. "
                f"Available products: {available}"
            )
        if len(matches) > 1:
            raise ValueError(
                f"Product name '{product_name}' is duplicated in '{product_group}'"
            )
        return deepcopy(matches[0])
