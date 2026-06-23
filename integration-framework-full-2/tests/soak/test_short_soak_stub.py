import pytest
import time

@pytest.mark.soak
def test_short_soak_stub(vehicle_system):
    vehicle_system.startup()
    time.sleep(0.01)
    assert vehicle_system.wait_until_healthy()
