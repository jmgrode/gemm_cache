class Packet:
    def __init__(self, load: bool, addr: int, size: 0 = int, data: None = int, latency: 0 = int) -> None:
        self.load = load # whether the packet is for a load or store
        self.addr = addr
        self.size = size # size in bytes
        self.data = data
        self.latency = latency
    