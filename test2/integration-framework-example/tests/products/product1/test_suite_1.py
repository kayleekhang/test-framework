import pytest

from framework.config.models import MediaSpec


pytestmark = [
    pytest.mark.product("product1"),
    pytest.mark.suite("suite1"),
]


@pytest.fixture
def product1(products):
    return products.get("product1")


@pytest.fixture
def product2(products):
    return products.get("product2")


@pytest.mark.requirement("REQ-001")
@pytest.mark.capability("send_udp")
@pytest.mark.network
def test_product1_sends_udp(product1, product2, traffic_capture, iteration):
    transmission = product1.backend.send_udp_request(receiver_ip=product2.config.ip, count=3)
    packets = traffic_capture.collect_for_transmission(transmission)

    product1.verify.assert_udp_sent_to(packets, product2.config.ip)
    assert packets.count_protocol("udp") == 3


@pytest.mark.requirement("REQ-002")
@pytest.mark.capability("receive_audio")
@pytest.mark.media
def test_product1_receives_multiple_audio_streams(product1):
    spec = MediaSpec(protocol="udp", media_type="audio", count=2)

    listener = product1.backend.receive_media(spec)

    assert listener == "product1:udp:audio:listening"


@pytest.mark.requirement("REQ-003")
@pytest.mark.capability("send_audio")
@pytest.mark.performance
@pytest.mark.media
def test_product1_sends_audio_under_load(product1, product2, traffic_capture, iteration):
    spec = MediaSpec(protocol="udp", media_type="audio", count=10)

    transmission = product1.backend.send_media(receiver_ip=product2.config.ip, spec=spec)
    packets = traffic_capture.collect_for_transmission(transmission)

    assert packets.has_route(product1.config.ip, product2.config.ip)
    assert packets.count_protocol("udp") == 10
