from packet import Packet, MatrixPacket
from memory import MemObject
from memory_array import MemoryArray
from dram import Dram

class GemmCache(MemObject):
    def __init__(self, matrix_dim: int, num_matrices: int, read_latency: int, write_latency: int, matmul_latency:int, matadd_latency: int) -> None:
        size = matrix_dim * matrix_dim * num_matrices # size is also addr_range
        super().__init__(size, size, read_latency, write_latency)
        self.matrix_dim = matrix_dim
        self.num_matrices = num_matrices
        self.matmul_latency = matmul_latency
        self.matadd_latency = matadd_latency
        self.matrices = MemoryArray(matrix_dim * matrix_dim * num_matrices)
        self.quantization = 1

    def process_packet(self, pkt: Packet) -> Packet:
        if pkt.load:
            pkt.data = 0
            for i in range(pkt.size):
                byte = self.matrices[pkt.addr+i]
                assert byte < 256
                pkt.data = (pkt.data << 8) | byte
            pkt.latency += self.read_latency # edit latency stuff
        else:
            for i in range(pkt.size):
                byte = (pkt.data >> ((pkt.size - i - 1) * 8)) & 0xff
                self.matrices[pkt.addr+i] = byte
            pkt.latency += self.write_latency
        return pkt
    
    def process_matrix_op_packet(self, pkt: MatrixPacket) -> MatrixPacket:
        if pkt.multiply:
            self.matrix_multiply(pkt.matA_start, pkt.matB_start, pkt.matC_start)
            pkt.latency += self.matmul_latency
        else:
            self.matrix_add(pkt.matA_start, pkt.matB_start, pkt.matC_start)
            pkt.latency += self.matadd_latency
    
    def matrix_multiply(self, matA_start: int, matB_start: int, matC_start: int) -> None:
        rows_A, cols_A = self.matrix_dim
        rows_B, cols_B = self.matrix_dim

        for i in range(rows_A):
            for j in range(cols_B):
                result = 0
                for k in range(cols_A):
                    matA_addr = matA_start + (i * cols_A + k) * 2
                    matB_addr = matB_start + (k * cols_B + j) * 2

                    valA = self.matrices.load(matA_addr, self.quantization)
                    valB = self.matrices.load(matB_addr, self.quantization)

                    result += valA * valB

                matC_addr = matC_start + (i * cols_B + j) * 2
                self.matrices.store(matC_addr, self.quantization, result)

    def matrix_add(self, matA_start: int, matB_start: int, matC_start: int) -> None:
        rows, cols = self.matrix_dim

        for i in range(rows):
            for j in range(cols):
                matA_addr = matA_start + (i * cols + j) * 2
                matB_addr = matB_start + (i * cols + j) * 2
                matC_addr = matC_start + (i * cols + j) * 2

                valA = self.matrices.load(matA_addr, self.quantization)
                valB = self.matrices.load(matB_addr, self.quantization)

                result = valA + valB

                self.matrices.store(matC_addr, self.quantization, result)

    def print_memory(self, starting_addr) -> None:
        self.matrices.print(starting_addr)

class Cache(MemObject):
    def __init__(self, size: int, addr_range: int, block_size: int, read_latency: int, write_latency: int, dram: Dram) -> None:
        super().__init__(size, addr_range, read_latency, write_latency)
        self.block_size = block_size
        self.cache = MemoryArray(size)
        self.tags = {}
        self.dram = dram     
    
    def process_packet(self, port: int, pkt: Packet) -> Packet:
        pkt_tag = pkt.addr & (~0xFF)
        cache_addr = pkt.addr & 0xF8
        if pkt.load:
            if cache_addr in self.tags and (self.tags[cache_addr] == pkt_tag):
                #return self.cache.load(cache_addr, pkt.size)
                pkt.data = self.cache.load(cache_addr, pkt.size)
                return pkt
            elif cache_addr in self.tags:
                evict_data = self.cache.load(cache_addr, self.block_size)
                evict_pkt = Packet(False, self.tags[cache_addr] + cache_addr, self.block_size, evict_data, 1)
                self.dram.process_packet(evict_pkt)
                self.tags.pop(cache_addr)
                new_data = self.dram.process_packet(pkt)
                self.cache.store(new_data.addr & 0xF8, new_data.size, new_data.data)
                self.tags[cache_addr]=pkt_tag
                return new_data
            else:
                new_data = self.dram.process_packet(pkt)
                self.cache.store(new_data.addr & 0xF8, new_data.size, new_data.data)
                self.tags[cache_addr]=pkt_tag
                return new_data
        else:
            if cache_addr in self.tags and (self.tags[cache_addr] == pkt_tag):
                self.cache.store(cache_addr, pkt.size, pkt.data)
                return pkt
            elif cache_addr in self.tags and (self.tags[cache_addr] != pkt_tag):
                evict_data = self.cache.load(cache_addr, self.block_size)
                evict_pkt = Packet(False, self.tags[cache_addr] + cache_addr, self.block_size, evict_data, 1)
                self.dram.process_packet(evict_pkt)
                self.tags.pop(cache_addr)
                self.cache.store(cache_addr, pkt.size, pkt.data)
                self.tags[cache_addr]=pkt_tag
                return pkt
            else:
                # Fully associative cache 
                if len(self.tags) >= self.size:
                    print("Should never hit this!!!")
                    # Evict some data if full and write it back to DRAM
                    eviction = self.cache.load(cache_addr)
                    self.dram.process_packet(eviction)
                    self.tags.pop(cache_addr)
                self.cache.store(cache_addr, pkt.size, pkt.data)
                self.tags[cache_addr]=pkt_tag
                return pkt

    def print(self, starting_addr: int) -> None:
        self.cache.print(starting_addr)

