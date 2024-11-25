from typing import Callable
from packet import Packet
from memory import MemObject

class GemmCache(MemObject):
    def __init__(self, matrix_size: int, num_matrices: int, ports: list[Callable], read_latency: int, write_latency: int, matmul_latency:int, matadd_latency: int) -> None:
        size = matrix_size * num_matrices # size is also addr_range
        super().__init__(size, size, ports, read_latency, write_latency)
        self.matrix_size = matrix_size
        self.num_matrices = num_matrices
        self.matmul_latency = matmul_latency
        self.matadd_latency = matadd_latency
        self.matrices = [[0 for i in range(matrix_size)] for i in range(num_matrices)]

    def process_packet(self, port: int, pkt: Packet) -> Packet:
        # TODO: implement loading and storing
        pass




class Cache(MemObject):
    def __init__(self, size: int, addr_range: int, ports: list[Callable], dram_port: int, read_latency: int, write_latency: int) -> None:
        super().__init__(size, addr_range, ports, read_latency, write_latency)
        self.dram_port = dram_port # port for fetching from memory
        self.cache = {}
        
    def process_packet(self, port: int, pkt: Packet) -> Packet:
        # TODO: handle fetching from memory and evictions
        pass

    def store(self, pkt: Packet) -> None:
        self.cache[pkt.addr] = pkt.data

    def retrieve(self, address: int) -> int:
        return self.cache[address]

