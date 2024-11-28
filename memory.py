from packet import Packet

class MemObject:
    def __init__(self, size: int, addr_range: int, read_latency: int, write_latency: int):
        self.size = size
        self.addr_range = addr_range # Size of address space held by MemObject; addr_range == size except for normal caches
        self.read_latency = read_latency
        self.write_latency = write_latency
    
    def process_packet(self, pkt: Packet) -> Packet:
        pass
