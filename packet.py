class Packet:
    def __init__(self, load: bool, addr: int, size: 0 = int, data: None = int, latency: 0 = int, from_DRAM: False = bool) -> None:
        self.load = load # whether the packet is for a load or store
        self.addr = addr
        self.size = size # size in bytes
        self.data = data
        self.latency = latency
        self.from_DRAM = from_DRAM

class MatrixPacket:
    def __init__(self, multiply: bool, matA_start: int, matB_start: int, matC_start: int, dimA: tuple[int, int], dimB: tuple[int, int], latency: 0 = int) -> None:
        self.multiply = multiply # whether the packet is for multiply or add
        self.matA_start = matA_start
        self.matB_start = matB_start
        self.matC_start = matC_start
        self.dimA = dimA
        self.dimB = dimB
        self.latency = latency

    