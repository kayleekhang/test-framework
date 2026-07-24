from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Iterable

from api import API, Endpoint
from factory import ProbeFactory, WebSocketFactory
from ui.pages import Page
from ui.selenium import SeleniumWrapper


class PageBuilder:
    def __init__(self, name: str, route: str):
        self.name = name
        self.route = route
        self.elements: dict[str, dict[str, Any]] = {}

    def element(
        self,
        name: str,
        *,
        element_type: str = "text",
        test_tag: str | None = None,
        selector: str | None = None,
        **options: Any,
    ) -> PageBuilder:
        if not test_tag and not selector:
            raise ValueError("An element needs test_tag or selector")
        config = {"type": element_type, **options}
        if test_tag:
            config["test_tag"] = test_tag
        if selector:
            config["selector"] = selector
        self.elements[name] = config
        return self

    def button(self, name: str, *, test_tag: str, **options: Any) -> PageBuilder:
        return self.element(name, element_type="button", test_tag=test_tag, **options)

    def popup(self, name: str, *, test_tag: str, **options: Any) -> PageBuilder:
        return self.element(name, element_type="popup", test_tag=test_tag, **options)

    def text(self, name: str, *, test_tag: str, **options: Any) -> PageBuilder:
        return self.element(name, element_type="text", test_tag=test_tag, **options)

    def build(self, driver: Any, base_url: str, selector_suffix: str = "") -> Page:
        return Page(
            driver=driver,
            base_url=base_url,
            product_prefix="",
            selector_suffix=selector_suffix,
            name=self.name,
            config={"route": self.route, "elements": deepcopy(self.elements)},
        )


class ProductBuilder:
    def __init__(self, product_type: str):
        self.product_type = product_type
        self.api_endpoints: dict[str, dict[str, Any]] = {}
        self.api_headers: dict[str, str] = {}
        self.pages: dict[str, PageBuilder] = {}
        self.probe_configs: dict[str, dict[str, Any]] = {}
        self.websocket_configs: dict[str, dict[str, Any]] = {}
        self.ui_config: dict[str, Any] | None = None

    def with_api_endpoint(self, name: str, **config: Any) -> ProductBuilder:
        self.api_endpoints[name] = config
        return self

    def with_api_headers(self, **headers: str) -> ProductBuilder:
        self.api_headers.update(headers)
        return self

    def with_ui(
        self,
        *,
        protocol: str = "https",
        port: int = 8080,
        selenium: dict[str, Any] | None = None,
    ) -> ProductBuilder:
        self.ui_config = {
            "protocol": protocol,
            "port": port,
            "selenium": deepcopy(selenium or {}),
        }
        return self

    def with_page(self, page: PageBuilder) -> ProductBuilder:
        self.pages[page.name] = page
        return self

    def with_probe(self, name: str, **config: Any) -> ProductBuilder:
        self.probe_configs[name] = config
        return self

    def with_websocket(self, name: str, **config: Any) -> ProductBuilder:
        self.websocket_configs[name] = config
        return self

    def build(
        self,
        *,
        name: str,
        ip: str,
        driver: Any = None,
        operation: dict[str, Any] | None = None,
    ):
        from products import Product

        operation = deepcopy(operation or {})
        operation.update({"name": name, "ip": ip})
        endpoints = {
            endpoint_name: Endpoint(host=ip, **deepcopy(config))
            for endpoint_name, config in self.api_endpoints.items()
        }
        api = API(endpoints=endpoints, base_headers=deepcopy(self.api_headers))

        selenium = None
        pages = {}
        if self.ui_config is not None:
            protocol = operation.get("ui_protocol", self.ui_config["protocol"])
            port = operation.get("ui_port", self.ui_config["port"])
            base_url = f"{protocol}://{ip}:{port}"
            selenium = SeleniumWrapper(
                base_url=base_url,
                config=deepcopy(self.ui_config["selenium"]),
                driver=driver,
            )
            pages = {
                page_name: page.build(selenium, base_url, selector_suffix=name)
                for page_name, page in self.pages.items()
            }

        probes = {
            probe_name: ProbeFactory.create(probe_name, deepcopy(config))
            for probe_name, config in self.probe_configs.items()
        }
        websockets = {
            channel_name: WebSocketFactory.create(
                channel_name, deepcopy(config), host=ip
            )
            for channel_name, config in self.websocket_configs.items()
        }
        return Product(
            name=name,
            ip=ip,
            product_type=self.product_type,
            operational_config=operation,
            api=api,
            pages=pages,
            probes=probes,
            websockets=websockets,
            selenium=selenium,
        )

    def build_many(
        self,
        operations: Iterable[dict[str, Any]],
        driver_builder: Callable[[dict[str, Any]], Any] | None = None,
    ) -> list:
        products = []
        for operation in operations:
            if "name" not in operation or not (operation.get("ip") or operation.get("host")):
                raise ValueError("Each operation needs name and ip (or host)")
            driver = driver_builder(operation) if driver_builder else None
            products.append(
                self.build(
                    name=operation["name"],
                    ip=operation.get("ip") or operation["host"],
                    driver=driver,
                    operation=operation,
                )
            )
        return products


def build_products_from_config(
    operational_config: dict[str, Any],
    builders: dict[str, ProductBuilder],
    driver_builder: Callable[[dict[str, Any]], Any] | None = None,
) -> dict[str, list]:
    """Build all configured instances using caller-provided builder definitions."""
    built = {}
    for group_name, group_config in operational_config.items():
        builder_name = group_config["builder"]
        if builder_name not in builders:
            available = ", ".join(sorted(builders)) or "none"
            raise KeyError(
                f"Unknown builder '{builder_name}'. Available builders: {available}"
            )
        built[group_name] = builders[builder_name].build_many(
            group_config.get("instances", []), driver_builder=driver_builder
        )
    return built
