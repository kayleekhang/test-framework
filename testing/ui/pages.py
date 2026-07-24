from __future__ import annotations

from typing import Any

from factory import ElementFactory
from ui.elements import UiElement, WebDriver


class Page:
    def __init__(
        self,
        driver: WebDriver,
        base_url: str,
        product_prefix: str,
        selector_suffix: str,
        name: str,
        config: dict[str, Any],
    ):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.product_prefix = product_prefix
        self.selector_suffix = selector_suffix
        self.name = name
        self.config = config
        self.route = config["route"]
        self.elements = {
            element_name: ElementFactory.create(
                driver=driver,
                product_prefix=product_prefix,
                selector_suffix=selector_suffix,
                name=element_name,
                config=element_config,
            )
            for element_name, element_config in config.get("elements", {}).items()
        }

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.route}"

    def open(self):
        self.driver.get(self.url)
        return self

    def element(self, name: str) -> UiElement:
        return self.elements[name]

    def click(self, name: str):
        self.element(name).click()

    def text(self, name: str) -> str:
        return self.element(name).text()

    def is_visible(self, name: str) -> bool:
        return self.element(name).is_visible()
