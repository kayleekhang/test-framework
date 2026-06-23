from framework.systems.vehicle.vehicle_system import VehicleSystem
from framework.systems.security.security_system import SecuritySystem
from framework.systems.communications.communications_system import CommunicationsSystem
from framework.systems.radar.radar_system import RadarSystem
from framework.systems.gateway.gateway_system import GatewaySystem

class SystemFactory:
    @staticmethod
    def create(config):
        systems = {
            "vehicle": VehicleSystem,
            "security": SecuritySystem,
            "communications": CommunicationsSystem,
            "radar": RadarSystem,
            "gateway": GatewaySystem,
        }
        if config.system_type not in systems:
            raise ValueError(f"Unknown system_type: {config.system_type}")
        return systems[config.system_type](config)
