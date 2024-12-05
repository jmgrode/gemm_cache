# packet.py

class Packet:
    def __init__(self, load: bool, addr: int, size: int = 0, data: int = None, latency: int = 0) -> None:
        self.load = load # whether the packet is for a load or store
        self.addr = addr
        self.size = size # size in bytes
        self.data = data
        self.latency = latency

class MatrixPacket:
    def __init__(self, multiply: bool, matA_start: int, matB_start: int, matC_start: int, latency: int = 0) -> None:
        self.multiply = multiply # whether the packet is for multiply or add
        self.matA_start = matA_start
        self.matB_start = matB_start
        self.matC_start = matC_start
        self.latency = latency

    