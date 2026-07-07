from framework.config.models import ProductConfig
from framework.network.capture import PacketSet
from framework.products.base import ProductVerifier


class Product1Verifier(ProductVerifier):
    def __init__(self, config: ProductConfig):
        super().__init__(config)

    def assert_udp_sent_to(self, packets: PacketSet, receiver_ip: str) -> None:
        assert packets.has_protocol("udp")
        assert packets.has_route(self.config.ip, receiver_ip)
