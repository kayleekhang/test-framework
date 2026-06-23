from framework.systems.base_system import BaseSystem
from framework.factory.product_factory import ProductFactory

class VehicleSystem(BaseSystem):
    def __init__(self, config):
        products = {p.name: ProductFactory.create(p) for p in config.products}
        super().__init__(config, products)

        self.gps = products["gps"]
        self.radio = products["radio"]
        self.controller = products["controller"]

    def nominal_mission_flow(self):
        self.gps.publish_position(28.0, -82.0)
        self.controller.command("NAVIGATE")
        self.radio.transmit("MISSION_STATE_OK")
