from typing import Callable
from packet import Packet

class Dram:
    def __init__(self, size: int, ports: list[Callable],
                 read_latency: int, write_latency: int) -> None:
        self.memory = {}
        self.ports = ports # function which sends packet back across port
        self.size = size
        self.read_latency = read_latency
        self.write_latency = write_latency

    def recv_packet(self, port: int, pkt: Packet) -> None:
        self.ports[port](pkt)
        pass
    