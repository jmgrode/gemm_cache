from packet import Packet
from memory import MemObject

class Cpu:
    def __init__(self, memories: list[MemObject], num_registers: int, register_bytes: int, gemm_port: int) -> None:
        self.memories = memories # list of gemm_caches and drams directly connected to cpu
        self.registers = [0 for i in range(num_registers)]
        self.register_mask = [0xff][register_bytes-1] # length of each register in number of bytes
        # each memory the cpu is connected to will contain addr_range part of the address space
        # eg if memories[0].addr_range = 1024 and memories[1].addr_range = 256 then
        # memories[0] covers bytes [1023:0] and memories[1] covers [1279:1024]

    def load(self, dest_register: int, addr_register: int, immediate: int) -> None:
        # TODO: create a packet and send to corresponding memory
        pass

    def store(self, src_register: int, addr_register: int, immediate: int) -> None:
        # TODO: create a packet and send to corresponding memory
        pass

    def add_immediate(self, dest_register: int, src_register: int, immediate: int) -> None:
        self.registers[dest_register] = (self.registers[src_register] + immediate) & self.register_mask

    def add(self, dest_register: int, src_register1: int, src_register2: int) -> None:
        self.registers[dest_register] = (self.registers[src_register1] + self.registers[src_register2]) & self.register_mask

    def multiply(self, dest_register: int, src_register1: int, src_register2: int) -> None:
        self.registers[dest_register] = (self.registers[src_register1] * self.registers[src_register2]) & self.register_mask

    # TODO: determine how cpu should request matrix operations
    # TODO: add functions for printing out register and memory state
    

    def process_packet(self, port: int, pkt: Packet) -> Packet:
        # TODO: implement loading and storing
        pass
