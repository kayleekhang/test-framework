import pytest

from pytest_metadata import capabilities, products, requirements


@pytest.mark.probe
@pytest.mark.blackbox
@products("audio_device")
@capabilities("CAP-AUDIO-TRANSPORT")
@requirements("REQ-201", "REQ-202")
def test_cap_audio_transport_has_send_receive_and_capture_probes(audio_device_product):
    assert set(audio_device_product.probes) >= {
        "send_test_tone",
        "receive_audio",
        "audio_packets",
    }


@pytest.mark.api
@pytest.mark.probe
@pytest.mark.blackbox
@products("audio_device", "backend")
@capabilities("CAP-HEALTH-MONITORING")
@requirements("REQ-001", "REQ-201")
def test_cap_health_monitoring_has_health_endpoint(product_loader):
    backend = product_loader("backend")
    audio_device = product_loader("audio_device")

    assert backend.api.endpoint("health").path == "/health"
    assert audio_device.api.endpoint("health").path == "/health"
