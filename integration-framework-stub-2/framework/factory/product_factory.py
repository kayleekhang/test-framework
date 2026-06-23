from framework.products.gps.gps_product import GpsProduct
from framework.products.radio.radio_product import RadioProduct
from framework.products.controller.controller_product import ControllerProduct

class ProductFactory:
    @staticmethod
    def create(config):
        if config.product_type == "gps":
            return GpsProduct(config)

        if config.product_type == "radio":
            return RadioProduct(config)

        if config.product_type == "controller":
            return ControllerProduct(config)

        raise ValueError(f"Unknown product_type: {config.product_type}")
