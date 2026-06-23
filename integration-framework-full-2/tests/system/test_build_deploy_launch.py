import pytest
from pathlib import Path

@pytest.mark.system
def test_build_deploy_launch_lifecycle(built_vehicle_system):
    deploy_results = built_vehicle_system.deploy()
    built_vehicle_system.startup()
    assert built_vehicle_system.wait_until_healthy()
    assert "controller" in deploy_results
