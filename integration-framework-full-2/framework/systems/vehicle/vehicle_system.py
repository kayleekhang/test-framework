from framework.systems.base_system import BaseSystem

class VehicleSystem(BaseSystem):
    def __init__(self, config):
        super().__init__(config)
        self.gps = self.products["gps"]
        self.radio = self.products["radio"]
        self.controller = self.products["controller"]

    def nominal_mission_flow(self):
        self.gps.publish_position(28.0, -82.0)
        self.controller.command("NAVIGATE")
        self.radio.transmit("MISSION_STATE_OK")
