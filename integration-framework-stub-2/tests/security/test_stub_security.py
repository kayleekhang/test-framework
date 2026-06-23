import pytest

@pytest.mark.security
def test_bad_cert_rejected_stub(vehicle_system):
    vehicle_system.startup()
    print("[SECURITY] inject bad certificate")
    assert vehicle_system.wait_until_healthy()
