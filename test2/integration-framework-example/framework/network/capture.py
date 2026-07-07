from dataclasses import dataclass

from framework.media.gstreamer import MediaTransmission


@dataclass(frozen=True)
class Packet:
    protocol: str
    src: str
    dst: str
    src_port: int
    dst_port: int


class PacketSet:
    def __init__(self, packets: list[Packet]):
        self._packets = packets

    def has_protocol(self, protocol: str) -> bool:
        return any(packet.protocol == protocol for packet in self._packets)

    def count_protocol(self, protocol: str) -> int:
        return sum(1 for packet in self._packets if packet.protocol == protocol)

    def has_route(self, src: str, dst: str) -> bool:
        return any(packet.src == src and packet.dst == dst for packet in self._packets)


class PacketCapture:
    """Mock capture object.

    Real implementations can start tcpdump/tshark here and parse the pcap into
    the same PacketSet interface.
    """

    def collect_for_transmission(self, transmission: MediaTransmission) -> PacketSet:
        packets = [
            Packet(
                protocol=transmission.spec.protocol,
                src=transmission.sender.ip,
                dst=transmission.receiver_ip,
                src_port=transmission.spec.source_port,
                dst_port=transmission.spec.destination_port,
            )
            for _ in range(transmission.spec.count)
        ]
        return PacketSet(packets)
