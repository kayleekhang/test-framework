from framework.config.models import ProductConfig
from framework.media.gstreamer import GStreamer
from framework.products.base import Product
from framework.products.product1.backend import Product1Backend
from framework.products.product1.ui import Product1Ui
from framework.products.product1.verify import Product1Verifier


class Product1(Product):
    def __init__(self, config: ProductConfig):
        media = GStreamer()
        self.config = config
        self.backend = Product1Backend(config, media)
        self.ui = Product1Ui(config)
        self.verify = Product1Verifier(config)
