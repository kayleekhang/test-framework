from framework.config.models import EnvironmentConfig, MediaSpec, ProductConfig
from framework.media.gstreamer import GStreamer, MediaTransmission
from typing import Optional


class BackendClient:
    def __init__(self, config: ProductConfig, media: GStreamer):
        self.config = config
        self._media = media

    def send_media(self, receiver_ip: str, spec: MediaSpec) -> MediaTransmission:
        capability = f"send_{spec.media_type}" if spec.media_type != "data" else f"send_{spec.protocol}"
        if not (self.config.supports(capability) or self.config.supports(f"send_{spec.protocol}")):
            raise CapabilityError(f"{self.config.name} does not support {capability}")
        return self._media.send(self.config, receiver_ip, spec)

    def receive_media(self, spec: MediaSpec) -> str:
        capability = f"receive_{spec.media_type}" if spec.media_type != "data" else f"receive_{spec.protocol}"
        if not (self.config.supports(capability) or self.config.supports(f"receive_{spec.protocol}")):
            raise CapabilityError(f"{self.config.name} does not support {capability}")
        return self._media.receive(self.config, spec)


class UiClient:
    def __init__(self, config: ProductConfig):
        self.config = config

    def open(self, browser) -> None:
        if not self.config.ui_url:
            raise CapabilityError(f"{self.config.name} has no web UI")
        browser.get(self.config.ui_url)


class ProductVerifier:
    def __init__(self, config: ProductConfig):
        self.config = config

    def assert_capability(self, capability: str) -> None:
        assert self.config.supports(capability), f"{self.config.name} must support {capability}"


class Product:
    def __init__(self, config: ProductConfig, media: Optional[GStreamer] = None):
        self.config = config
        self.backend = BackendClient(config, media or GStreamer())
        self.ui = UiClient(config)
        self.verify = ProductVerifier(config)


class ProductRegistry:
    def __init__(self, products: dict[str, Product]):
        self._products = products

    @classmethod
    def from_environment(cls, environment: EnvironmentConfig) -> "ProductRegistry":
        products = {}
        for name, config in environment.products.items():
            if name == "product1":
                from framework.products.product1 import Product1

                products[name] = Product1(config)
            else:
                products[name] = Product(config)
        return cls(products)

    def get(self, name: str) -> Product:
        return self._products[name]

    def with_capability(self, capability: str) -> list[Product]:
        return [
            product
            for product in self._products.values()
            if product.config.supports(capability)
        ]


class CapabilityError(RuntimeError):
    pass
