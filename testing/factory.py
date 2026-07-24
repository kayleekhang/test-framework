"""Public home for the remaining low-level component factories.

Products and pages are assembled with builders. These factories only select
concrete adapters for elements, probes, and WebSocket channels.
"""

from typing import Any

from probes import ProbeFactory
from ui.elements import Button, By, Popup, UiElement, WebDriver
from websockets_client import WebSocketFactory


class ElementFactory:
    ELEMENT_TYPES = {"button": Button, "popup": Popup, "text": UiElement}

    @classmethod
    def create(
        cls,
        driver: WebDriver,
        product_prefix: str,
        selector_suffix: str,
        name: str,
        config: dict[str, Any],
    ) -> UiElement:
        element_cls = cls.ELEMENT_TYPES.get(config.get("type", "text"), UiElement)
        return element_cls(
            driver=driver,
            name=name,
            selector=cls._selector(product_prefix, selector_suffix, config),
            by=config.get("by", By.CSS_SELECTOR),
            timeout_seconds=config.get("timeout_seconds", 10),
        )

    @staticmethod
    def _selector(
        product_prefix: str, selector_suffix: str, config: dict[str, Any]
    ) -> str:
        if "selector" in config:
            return config["selector"]
        if "test_tag" in config:
            test_tag = config["test_tag"]
            if selector_suffix:
                test_tag = f"{test_tag}_{selector_suffix}"
            if product_prefix:
                test_tag = f"{product_prefix}-{test_tag}"
            return f'[data-testid="{test_tag}"]'
        raise ValueError(f"Element config needs selector or test_tag: {config}")

__all__ = ["ElementFactory", "ProbeFactory", "WebSocketFactory"]
