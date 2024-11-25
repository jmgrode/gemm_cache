from typing import Callable
from packet import Packet

class MemObject:
    def __init__(self, size: int, addr_range: int, ports: list[Callable], read_latency: int, write_latency: int):
        self.size = size
        self.addr_range = addr_range
        self.ports = ports # list of recv_packet functions from other objects
        self.read_latency = read_latency
        self.write_latency = write_latency
    
    def process_packet(self, port: int, pkt: Packet) -> None:
        pass
