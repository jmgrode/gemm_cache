from packet import Packet
from memory import MemObject

class CpuLatencies:
    def __init__(self) -> None:
        self.add_latency = 1
        self.multiply_latency = 3
        self.branch_latency = 1
        self.branch_taken_latency = 2
        self.jump_latency = 2
        self.logical_latency = 1

class Cpu:
    def __init__(self, memories: list[MemObject], num_registers: int, register_bytes: int, gemm_port: int, cpu_latencies: CpuLatencies) -> None:
        self.memories = memories # list of gemm_caches and drams directly connected to cpu
        self.registers = [0 for i in range(num_registers)]
        self.register_bytes = register_bytes
        self.register_mask = [0xff][register_bytes-1] # length of each register in number of bytes
        self.pc = 0
        self.cpu_latencies = cpu_latencies
        # each memory the cpu is connected to will contain addr_range part of the address space
        # eg if memories[0].addr_range = 1024 and memories[1].addr_range = 256 then
        # memories[0] covers bytes [1023:0] and memories[1] covers [1279:1024]
        # Cpu translates cpu address range into byte range of each MemObject
        # eg if accessing address 1024 and a is memory covering [2047:1024] then the packet contains addr = 0

    def load(self, dest_register: int, addr_register: int, immediate: int) -> int:
        ld_req_pkt = Packet(True, self.registers[addr_register]+immediate, self.register_bytes, None, 1)
        
        # Assuming cache is first memory in list
        ld_resp_pkt = self.memories[0].process_packet(ld_req_pkt)
        self.registers[dest_register] = ld_resp_pkt.data
        return ld_req_pkt.latency

    def store(self, src_register: int, addr_register: int, immediate: int) -> int:
        # TODO: create a packet and send to corresponding memory
        st_req_pkt = Packet(False, self.registers[addr_register]+immediate, self.register_bytes, self.registers[src_register], 1)
        st_resp_pkt = self.memories[0].process_packet(st_req_pkt)
        return  st_resp_pkt.latency

    def add_immediate(self, dest_register: int, src_register: int, immediate: int) -> int:
        self.registers[dest_register] = (self.registers[src_register] + immediate) & self.register_mask
        return self.cpu_latencies.add_latency

    def add(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.registers[dest_register] = (self.registers[src_register1] + self.registers[src_register2]) & self.register_mask
        return self.cpu_latencies.add_latency

    def multiply(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.registers[dest_register] = (self.registers[src_register1] * self.registers[src_register2]) & self.register_mask
        return self.cpu_latencies.multiply_latency

    # TODO: RISCV branch instruction (offset from current PC, immediate offset? register?)
    def branch_if(self, cond_register: int, offset_register: int) -> int:
        if self.registers[cond_register] == 1:
            self.pc = (self.pc + self.registers[offset_register]) & self.register_mask
            return self.cpu_latencies.branch_taken_latency
        return self.cpu_latencies.branch_latency

    # TODO: RSICV jump instruction (offset from current PC, immediate offset?)
    def jump(self, dest_register: int) -> int:
        self.pc = self.registers[dest_register] & self.register_mask
        return self.cpu_latencies.jump_latency

    def bitwise_or(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.registers[dest_register] = (self.registers[src_register1] | self.registers[src_register2]) & self.register_mask
        return self.cpu_latencies.logical_latency

     def bitwise_and(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.registers[dest_register] = (self.registers[src_register1] & self.registers[src_register2]) & self.register_mask
        return self.cpu_latencies.logical_latency

    def bitwise_xor(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.registers[dest_register] = (self.registers[src_register1] ^ self.registers[src_register2]) & self.register_mask
        return self.cpu_latencies.logical_latency

    def bitwise_nor(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.registers[dest_register] = (~(self.registers[src_register1] | self.registers[src_register2])) & self.register_mask
        return self.cpu_latencies.logical_latency

    # TODO: add functions for GeMMCache ops
    # TODO: add functions for printing out register and memory state
    def print_registers(self) -> None:
        print("Register State:")
        print(f"PC: 0x{self.pc:08x}")
        for i, value in enumerate(self.registers):
            print(f"R{i}: 0x{value:08x} ({value})")

