from typing import Callable
from packet import Packet
from memory import MemObject

class Dram(MemObject):
    def __init__(self, size: int, addr_range: int, ports: list[Callable],
                 read_latency: int, write_latency: int) -> None:
        super().__init__(size, addr_range, ports, read_latency, write_latency)
        self.memory = {}

    def recv_packet(self, port: int, pkt: Packet) -> None:
        # TODO: implement
        pass

    def store(self, pkt: Packet) -> None:
        self.memory[pkt.addr] = pkt.data

    def retrieve(self, address: int) -> int:
        return self.memory[address]
    