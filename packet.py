from typing import List

class Packet:
    def __init__(self, load: bool, addr: int, size: int, data: None = int) -> None:
        self.load = load # whether or not the packet is for a load or store
        self.addr = addr
        self.size = size
        self.data = data
    