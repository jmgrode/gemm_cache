# gemm_cache.py

from packet import Packet, MatrixPacket
from memory import MemObject
from memory_array import MemoryArray
from dram import Dram

class GemmCacheLatencies:
    def __init__(self, matrix_dim: int) -> None:
        # base latencies
        self.read_latency = 1
        self.write_latency = 1
        int8_add_latency = 0.5
        int8_multiply_latency = 0.5
        
        # intermediate calculations
        processing_element_latency = int8_add_latency + int8_multiply_latency
        systolic_array_latency = processing_element_latency * (3*matrix_dim - 1)

        self.matadd_latency = self.read_latency + int8_add_latency + self.write_latency
        self.matmul_latency = self.read_latency + systolic_array_latency + self.write_latency

class GemmCache(MemObject):
    def __init__(self, matrix_dim: int, num_matrices: int, addr_start: int, gemm_cache_latencies: GemmCacheLatencies, bytes_per_element: int = 1) -> None:
        size = matrix_dim * matrix_dim * num_matrices # size is also addr_range
        super().__init__(size, size, gemm_cache_latencies.read_latency, gemm_cache_latencies.write_latency)
        self.addr_range = addr_start + size
        self.matrix_dim = matrix_dim
        self.num_matrices = num_matrices
        self.matmul_latency = gemm_cache_latencies.matmul_latency
        self.matadd_latency = gemm_cache_latencies.matadd_latency
        self.matrices = MemoryArray(matrix_dim * matrix_dim * num_matrices)
        self.quantization = bytes_per_element

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
        assert pkt.matA_start % (self.matrix_dim * self.matrix_dim) == 0
        assert pkt.matB_start % (self.matrix_dim * self.matrix_dim) == 0
        assert pkt.matC_start % (self.matrix_dim * self.matrix_dim) == 0
        if pkt.multiply:
            self.matrix_multiply(pkt.matA_start, pkt.matB_start, pkt.matC_start)
            pkt.latency += self.matmul_latency
        else:
            self.matrix_add(pkt.matA_start, pkt.matB_start, pkt.matC_start)
            pkt.latency += self.matadd_latency
        return pkt
    
    def matrix_multiply(self, matA_start: int, matB_start: int, matC_start: int) -> None:
        rows_A = cols_A = cols_B = self.matrix_dim
        
        for i in range(rows_A):
            for j in range(cols_B):
                result = 0
                for k in range(cols_A):
                    matA_addr = matA_start + (i * cols_A + k) * self.quantization
                    matB_addr = matB_start + (k * cols_B + j) * self.quantization

                    valA = self.matrices.load(matA_addr, self.quantization)
                    valB = self.matrices.load(matB_addr, self.quantization)

                    result += valA * valB

                matC_addr = matC_start + (i * cols_B + j) * self.quantization
                self.matrices.store(matC_addr, self.quantization, result)

    def matrix_add(self, matA_start: int, matB_start: int, matC_start: int) -> None:
        rows = cols = self.matrix_dim
        
        for i in range(rows):
            for j in range(cols):
                matA_addr = matA_start + (i * cols + j) * self.quantization
                matB_addr = matB_start + (i * cols + j) * self.quantization
                matC_addr = matC_start + (i * cols + j) * self.quantization

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
    
    def evict_cache(self):
        for block_num, tag in self.tags.items():
            evict_pkt = Packet(False, tag + block_num, self.block_size, self.cache.load(block_num, self.block_size), 1)
            self.dram.process_packet(evict_pkt)

    def process_packet(self, pkt: Packet) -> Packet:
        pkt_tag = pkt.addr & (~0xFF)
        cache_addr = pkt.addr & 0xF8
        if pkt.load:
            if cache_addr in self.tags and (self.tags[cache_addr] == pkt_tag):
                pkt.data = self.cache.load(pkt.addr & (0xFF), pkt.size)
                return pkt
            elif cache_addr in self.tags:
                # Evict data in set
                evict_data = self.cache.load(cache_addr, self.block_size)
                evict_pkt = Packet(False, self.tags[cache_addr] + cache_addr, self.block_size, evict_data, 1)
                self.dram.process_packet(evict_pkt)
                self.tags.pop(cache_addr)

                # Ask DRAM for Data block
                dram_pkt = Packet(pkt.load, pkt.addr & (~0x7), self.block_size, pkt.data, pkt.latency)
                new_data = self.dram.process_packet(dram_pkt)

                # Store DRAM's block into cache, add to tag array, and return loaded data
                self.cache.store(new_data.addr & 0xF8, new_data.size, new_data.data)
                self.tags[cache_addr]=pkt_tag
                pkt.data = self.cache.load(pkt.addr & (0xFF), pkt.size)
                pkt.latency += new_data.latency
                return pkt
            else:
                # Ask DRAM for Data block
                dram_pkt = Packet(pkt.load, pkt.addr & (~0x7), self.block_size, pkt.data, pkt.latency)
                new_data = self.dram.process_packet(dram_pkt)

                # Store DRAM's block into cache, add to tag array, and return loaded data
                self.cache.store(new_data.addr & 0xF8, new_data.size, new_data.data)
                self.tags[cache_addr]=pkt_tag
                pkt.data = self.cache.load(pkt.addr & (0xFF), pkt.size)
                pkt.latency += new_data.latency
                return pkt
        else:
            if cache_addr in self.tags and (self.tags[cache_addr] == pkt_tag):
                self.cache.store(pkt.addr & (0xFF), pkt.size, pkt.data)
                return pkt
            elif cache_addr in self.tags and (self.tags[cache_addr] != pkt_tag):
                # Evict data in set
                evict_data = self.cache.load(cache_addr, self.block_size)
                evict_pkt = Packet(False, self.tags[cache_addr] + cache_addr, self.block_size, evict_data, 1)
                self.dram.process_packet(evict_pkt)
                self.tags.pop(cache_addr)

                # Ask DRAM for Data block
                dram_pkt = Packet(True, pkt.addr & (~0x7), self.block_size, pkt.data, pkt.latency)
                new_data = self.dram.process_packet(dram_pkt)

                # Store DRAM's data in the cache and then store the requested data into cache
                self.cache.store(new_data.addr & 0xF8, new_data.size, new_data.data)
                self.cache.store(pkt.addr & (0xFF), pkt.size, pkt.data)
                self.tags[cache_addr]=pkt_tag
                pkt.latency += new_data.latency
                return pkt
            else:
                # Ask DRAM for Data block
                dram_pkt = Packet(True, pkt.addr & (~0x7), self.block_size, pkt.data, pkt.latency)
                new_data = self.dram.process_packet(dram_pkt)

                # Store DRAM's data in the cache and then store the requested data into cache
                self.cache.store(new_data.addr & 0xF8, new_data.size, new_data.data)
                self.cache.store(pkt.addr & (0xFF), pkt.size, pkt.data)
                self.tags[cache_addr]=pkt_tag
                pkt.latency += new_data.latency
                return pkt

    def print(self, starting_addr: int) -> None:
        self.cache.print(starting_addr)

