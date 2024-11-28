from typing import Callable
from packet import Packet
from memory import MemObject
from memory_array import MemoryArray

class GemmCache(MemObject):
    def __init__(self, matrix_size: int, num_matrices: int, ports: list[Callable], read_latency: int, write_latency: int, matmul_latency:int, matadd_latency: int) -> None:
        size = matrix_size * num_matrices # size is also addr_range
        super().__init__(size, size, ports, read_latency, write_latency)
        self.matrix_size = matrix_size
        self.num_matrices = num_matrices
        self.matmul_latency = matmul_latency
        self.matadd_latency = matadd_latency
        self.matrices = [[0 for _ in range(matrix_size)] for _ in range(num_matrices)] # each element is a byte

    def process_packet(self, pkt: Packet) -> Packet:
        if pkt.load:
            pkt.data = 0
            for i in range(pkt.size):
                byte = self.matrices[pkt.addr+i]
                assert byte < 256
                pkt.data = (pkt.data << 8) | byte
                pkt.latency += self.read_latency
        else:
            for i in range(pkt.size):
                byte = (pkt.data >> ((pkt.size - i - 1) * 8)) & 0xff
                self.matrices[pkt.addr+i] = byte
                pkt.latency += self.write_latency
        return pkt
    
    def matrix_multiply(self) -> None:
        pass # TODO: add arguments and implement

    def matrix_add(self) -> None:
        pass # TODO: add arguments and implement

class Cache(MemObject):
    def __init__(self, size: int, addr_range: int, block_size: int, ports: list[Callable], dram_port: int, read_latency: int, write_latency: int) -> None:
        super().__init__(size, addr_range, ports, read_latency, write_latency)
        self.block_size = block_size
        self.dram_port = dram_port # port for fetching from memory
        #self.cache = {}
        #self.meta_data = {}
        self.cache = MemoryArray(size)
        self.tags = set()            
    
    def process_packet(self, port: int, pkt: Packet) -> Packet:
        # TODO: handle fetching from memory and evictions
        pkt_tag = pkt.addr & (~0xFF)
        if pkt.load:
            if pkt_tag in self.tags:
                return self.cache.load(pkt.addr, pkt.size)
            else:
                new_data = self.dram_port.process_packet(pkt)
                self.cache.store(new_data.addr, new_data.size, new_data.data)
                self.tags.add(pkt_tag)
                return new_data
        else:
            if len(self.tags) >= self.size:
                eviction = self.cache.load(pkt.addr)
                self.tags.remove(pkt_tag)
            self.cache.store(pkt.addr, pkt.size, pkt.data)
            self.tags.add(pkt_tag)


