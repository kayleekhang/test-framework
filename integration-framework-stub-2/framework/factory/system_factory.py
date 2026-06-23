from framework.systems.vehicle_system import VehicleSystem

class SystemFactory:
    @staticmethod
    def create(config):
        if config.system_type == "vehicle":
            return VehicleSystem(config)

        raise ValueError(f"Unknown system_type: {config.system_type}")
