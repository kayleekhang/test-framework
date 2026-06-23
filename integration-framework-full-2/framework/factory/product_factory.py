from framework.products.controller.controller_product import ControllerProduct
from framework.products.radio.radio_product import RadioProduct
from framework.products.gps.gps_product import GpsProduct
from framework.products.camera.camera_product import CameraProduct
from framework.products.display.display_product import DisplayProduct
from framework.products.gateway.gateway_product import GatewayProduct
from framework.products.tpm.tpm_product import TpmProduct
from framework.products.nats.nats_product import NatsProduct
from framework.products.database.database_product import DatabaseProduct

class ProductFactory:
    @staticmethod
    def create(config):
        products = {
            "controller": ControllerProduct,
            "radio": RadioProduct,
            "gps": GpsProduct,
            "camera": CameraProduct,
            "display": DisplayProduct,
            "gateway": GatewayProduct,
            "tpm": TpmProduct,
            "nats": NatsProduct,
            "database": DatabaseProduct,
        }
        if config.product_type not in products:
            raise ValueError(f"Unknown product_type: {config.product_type}")
        return products[config.product_type](config)
