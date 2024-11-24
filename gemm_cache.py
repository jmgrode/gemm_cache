from typing import Callable
import packet.Packet as Packet

class GemmCache:
    def __init__(self, matrix_size: int, num_matrices: int, send_packet: Callable, read_latency: int, write_latency: int, matmul_latency:int, matadd_latency: int):        self.matrix_size = matrix_size
        self.num_matrices = num_matrices
        self.send_packet = send_packet
        read_latency = read_latency
		self.write_latency = write_latency
		self.matmul_latency = matmul_latency
		self.matadd_latency = matadd_latency -> None:
        Packet pkt
        self.cache_size = matrix_size * num_matrices
        self.read_latency = read_latency
        self.write_latency = write_latency
        self.matmul_latency = matmul_latency
        self.matadd_latency = matadd_latency

    def recv_packet(self, pkt: Packet) -> None:
        pass

    def send_packet(self, pkt: Packet) -> None:
        pass

class Cache:
    def __init__(self, size: int = 4096) -> None:
        self.size = size
        self.cache = []

    def store(self, pkt: Packet) -> None:
        self.cache[pkt.addr] = pkt.data

    def retrieve(self, address: int) -> int:
        return self.cache[address]

