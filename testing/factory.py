from typing import Any

from api import API, Endpoint
from probes import ProbeFactory
from products import AudioDeviceProduct, BackendOnlyProduct, DisplayProduct, Product
from ui.elements import WebDriver
from ui.pages import Page, PageFactory


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
