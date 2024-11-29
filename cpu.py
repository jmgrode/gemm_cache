from packet import Packet
from memory import MemObject

class Cpu:
    def __init__(self, memories: list[MemObject], num_registers: int, register_bytes: int, gemm_port: int) -> None:
        self.memories = memories # list of gemm_caches and drams directly connected to cpu
        self.registers = [0 for i in range(num_registers)]
        self.register_mask = [0xff][register_bytes-1] # length of each register in number of bytes
        self.pc = 0
        # each memory the cpu is connected to will contain addr_range part of the address space
        # eg if memories[0].addr_range = 1024 and memories[1].addr_range = 256 then
        # memories[0] covers bytes [1023:0] and memories[1] covers [1279:1024]
        # Cpu translates cpu address range into byte range of each MemObject
        # eg if accessing address 1024 and a is memory covering [2047:1024] then the packet contains addr = 0

    def load(self, dest_register: int, addr_register: int, immediate: int) -> None:
        ld_req_pkt = Packet(1, self.registers[addr_register]+immediate, self.register_mask, None, 1)
        
        # Assuming cache is first memory in list
        ld_resp_pkt = self.memories[0].process_packet(ld_req_pkt)
        self.registers[dest_register] = ld_resp_pkt.data

    def store(self, src_register: int, addr_register: int, immediate: int) -> None:
        # TODO: create a packet and send to corresponding memory
        st_req_pkt = Packet(0, self.registers[addr_register]+immediate, self.register_mask, self.registers[src_register], 1)
        self.memories[0].process_packet(st_req_pkt)

    def add_immediate(self, dest_register: int, src_register: int, immediate: int) -> None:
        self.registers[dest_register] = (self.registers[src_register] + immediate) & self.register_mask

    def add(self, dest_register: int, src_register1: int, src_register2: int) -> None:
        self.registers[dest_register] = (self.registers[src_register1] + self.registers[src_register2]) & self.register_mask

    def multiply(self, dest_register: int, src_register1: int, src_register2: int) -> None:
        self.registers[dest_register] = (self.registers[src_register1] * self.registers[src_register2]) & self.register_mask

    # TODO: RISCV branch instruction (offset from current PC, immediate offset? register?)
    # TODO: RSICV jump instruction (offset from current PC, immediate offset?)

    # TODO: add functions for GeMMCache ops
    # TODO: add functions for printing out register and memory state

    def process_packet(self, port: int, pkt: Packet) -> Packet:
        # TODO: implement loading and storing
        pass
