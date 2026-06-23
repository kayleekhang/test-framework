from framework.factory.config_loader import ConfigLoader
from framework.factory.system_factory import SystemFactory

config = ConfigLoader.load_system("configs/systems/vehicle_system.yaml")
system = SystemFactory.create(config)

try:
    system.startup()
    system.nominal_mission_flow()
finally:
    system.collect_artifacts()
    system.shutdown()
