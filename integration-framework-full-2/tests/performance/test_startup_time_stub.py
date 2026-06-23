import pytest
import time

@pytest.mark.performance
def test_startup_time_stub(vehicle_system):
    start = time.time()
    vehicle_system.startup()
    assert time.time() - start < 5
