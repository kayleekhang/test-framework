from pathlib import Path
import pytest
from framework.factory.config_loader import ConfigLoader
from framework.factory.system_factory import SystemFactory

@pytest.mark.system
def test_build_vehicle_system_for_vm(tmp_path):
    config = ConfigLoader.load_system("configs/systems/vehicle_system.yaml", target_override="vm")
    system = SystemFactory.create(config)

    artifacts = system.build(tmp_path / "build")

    assert "gps" in artifacts
    assert "radio" in artifacts
    assert "controller" in artifacts
    assert any(Path(a).exists() for a in artifacts["controller"])
