import pytest
from framework.factory.config_loader import ConfigLoader
from framework.factory.system_factory import SystemFactory

@pytest.fixture
def vehicle_system():
    config = ConfigLoader.load_system("configs/systems/vehicle_system.yaml")
    system = SystemFactory.create(config)
    yield system
    system.collect_artifacts()
    system.shutdown()

@pytest.fixture
def built_vehicle_system():
    config = ConfigLoader.load_system("configs/systems/vehicle_system.yaml")
    system = SystemFactory.create(config)
    system.build()
    yield system
    system.collect_artifacts()
    system.shutdown()
