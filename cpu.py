# cpu.py

from typing import Callable
from packet import Packet, MatrixPacket
from memory import MemObject
from program import Program

class CpuLatencies:
    def __init__(self) -> None:
        self.add_latency = 1
        self.multiply_latency = 3
        self.branch_latency = 1
        self.jump_latency = 2
        self.logical_latency = 1

class Cpu:
    def __init__(self, memories: list[MemObject], num_registers: int, register_bytes: int, gemm_port: int, cpu_latencies: CpuLatencies) -> None:
        self.memories = memories # list of gemm_caches and drams directly connected to cpu
        self.registers = [0 for i in range(num_registers)]
        self.register_bytes = register_bytes
        self.register_mask = [0xff, 0xffff, 0xffffff, 0xffffffff][register_bytes-1] # length of each register in number of bytes
        self.cpu_latencies = cpu_latencies
        self.pc = 0
        self.time = 0
        # each memory the cpu is connected to will contain addr_range part of the address space
        # eg if memories[0].addr_range = 1024 and memories[1].addr_range = 256 then
        # memories[0] covers bytes [1023:0] and memories[1] covers [1279:1024]
        # Cpu translates cpu address range into byte range of each MemObject
        # eg if accessing address 1024 and a is memory covering [2047:1024] then the packet contains addr = 0

    def run_program(self, program: Program):
        # instructions is a list of tuples with instruction name string followed by operands, e.g. ("add", 1, 2)
        instructions = program.get_instructions()
        while instructions[self.pc][0] != "halt":
            instruction = instructions[self.pc]
            instr_func = self.get_instruction(instruction[0])
            self.time += instr_func(*instruction[1:])
            self.pc = self.pc + 1
            # print("PC: ", self.pc)
        print(f"Halted at cycle {self.time}")

    def get_instruction(self, instruction: str) -> Callable:
        instruction_dict = {
            "load": self.load,
            "store": self.store,
            "move_memory": self.move_memory,
            "move": self.move,
            "add": self.add,
            "add_immediate": self.add_immediate,
            "multiply": self.multiply,
            "branch_if": self.branch_if,
            "jump": self.jump,
            "bitwise_or": self.bitwise_or,
            "bitwise_and": self.bitwise_and,
            "bitwise_xor": self.bitwise_xor,
            "bitwise_nor": self.bitwise_nor,
            "bitwise_not": self.bitwise_not,
            "logical_shift_left": self.logical_shift_left,
            "logical_shift_right": self.logical_shift_right,
            "matrix_multiply": self.matrix_multiply,
            "matrix_add": self.matrix_add
        }
        return instruction_dict[instruction]

    def load(self, dest_register: int, addr_register: int, immediate: int) -> int:
        full_address = (self.registers[addr_register] + immediate) & self.register_mask
        memory_idx,addr = self.translate_addr(full_address)
        ld_req_pkt = Packet(True, addr, self.register_bytes, None, 1)
        
        ld_resp_pkt = self.memories[memory_idx].process_packet(ld_req_pkt)
        self.registers[dest_register] = ld_resp_pkt.data
        # print(f"LOAD: r{dest_register} <- MEM[{full_address}] = {ld_resp_pkt.data}")
        return ld_req_pkt.latency

    def store(self, src_register: int, addr_register: int, immediate: int) -> int:
        full_address = (self.registers[addr_register] + immediate) & self.register_mask
        memory_idx,addr = self.translate_addr(full_address)
        st_req_pkt = Packet(False, addr, self.register_bytes, self.registers[src_register], 1)
        # print(f"STORE: MEM[{full_address}] <- r{src_register} ({self.registers[src_register]})")
        st_resp_pkt = self.memories[memory_idx].process_packet(st_req_pkt)
        return st_resp_pkt.latency

    def move_memory(self, src_addr_register: int, dest_addr_register: int, size_register: int) -> None:
        src_full_address = (self.registers[src_addr_register]) & self.register_mask
        src_memory_idx, src_addr = self.translate_addr(src_full_address)

        dest_full_address = (self.registers[dest_addr_register]) & self.register_mask
        dest_memory_idx, dest_addr = self.translate_addr(dest_full_address)

        size = self.registers[size_register]

        ld_req_pkt = Packet(True, src_addr, size)
        ld_resp_pkt = self.memories[src_memory_idx].process_packet(ld_req_pkt)

        st_req_pkt = Packet(False, dest_addr, size, ld_resp_pkt.data, ld_resp_pkt.latency)
        st_resp_pkt = self.memories[dest_memory_idx].process_packet(st_req_pkt)
        return st_resp_pkt.latency

    def move(self, dest_register: int, immediate: int) -> int:
        self.registers[dest_register] = immediate & self.register_mask
        return self.cpu_latencies.logical_latency

    def add_immediate(self, dest_register: int, src_register: int, immediate: int) -> int:
        self.registers[dest_register] = (self.registers[src_register] + immediate) & self.register_mask
        return self.cpu_latencies.add_latency

    def add(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.registers[dest_register] = (self.registers[src_register1] + self.registers[src_register2]) & self.register_mask
        # print(f"ADD: r{dest_register} = r{src_register1} ({self.registers[src_register1]}) + r{src_register2} ({self.registers[src_register2]}) = {self.registers[dest_register]}")
        return self.cpu_latencies.add_latency

    def multiply(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.registers[dest_register] = (self.registers[src_register1] * self.registers[src_register2]) & self.register_mask
        # print(f"MUL: r{dest_register} = r{src_register1} ({self.registers[src_register1]}) * r{src_register2} ({self.registers[src_register2]}) = {self.registers[dest_register]}")
        return self.cpu_latencies.multiply_latency

    def branch_if(self, cond_register: int, immediate: int) -> int:
        if self.registers[cond_register] != 0:
            self.pc = self.pc + immediate - 1 # -1 to account for +1 in run_program
        return self.cpu_latencies.branch_latency

    def jump(self, dest_register: int) -> int:
        self.pc = self.registers[dest_register] - 1 # -1 to account for +1 in run_program
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
    
    def bitwise_not(self, dest_register: int, src_register: int) -> int:
        self.registers[dest_register] = (~(self.registers[src_register])) & self.register_mask
        return self.cpu_latencies.logical_latency
    
    def logical_shift_left(self, dest_register: int, value_register: int, shift_size_immediate: int) -> int:
        self.registers[dest_register] = (self.registers[value_register] << shift_size_immediate) & self.register_mask
        return self.cpu_latencies.logical_latency

    def logical_shift_right(self, dest_register: int, value_register: int, shift_size_immediate: int) -> int:
        self.registers[dest_register] = (self.registers[value_register] >> shift_size_immediate) & self.register_mask
        return self.cpu_latencies.logical_latency

    def matrix_multiply(self, dest_addr_register: int, src_addr_register1: int, src_addr_register2: int) -> int:
        # memory_idx should be the same for all 3 since they should be in same GeMMCache
        memory_idx,dest_addr = self.translate_addr(self.registers[dest_addr_register])
        memory_idx,src1_addr = self.translate_addr(self.registers[src_addr_register1])
        memory_idx,src2_addr = self.translate_addr(self.registers[src_addr_register2])
        mm_req_pkt = MatrixPacket(True, src1_addr, src2_addr, dest_addr)
        mm_resp_pkt = self.memories[memory_idx].process_matrix_op_packet(mm_req_pkt)
        return mm_resp_pkt.latency

    def matrix_add(self, dest_addr_register: int, src_addr_register1: int, src_addr_register2: int) -> int:
        # memory_idx should be the same for all 3 since they should be in same GeMMCache
        memory_idx,dest_addr = self.translate_addr(self.registers[dest_addr_register])
        memory_idx,src1_addr = self.translate_addr(self.registers[src_addr_register1])
        memory_idx,src2_addr = self.translate_addr(self.registers[src_addr_register2])
        ma_req_pkt = MatrixPacket(False, src1_addr, src2_addr, dest_addr)
        ma_resp_pkt = self.memories[memory_idx].process_matrix_op_packet(ma_req_pkt)
        return ma_resp_pkt.latency
    
    def print_registers(self) -> None:
        print("Register State:")
        print(f"PC: 0x{self.pc:08x}")
        for i, value in enumerate(self.registers):
            print(f"R{i}: 0x{value:08x} ({value})")

    def print_memory(self) -> None:
        print("Memory State:")
        current_range = 0
        for mem_idx,mem in enumerate(self.memories):
            print(f"Memory Object {mem_idx}")
            mem.print(current_range)
            current_range += mem.addr_range
                
    # translate memory address to memories index and address inside memories[index]
    def translate_addr(self, addr: int) -> tuple[int,int]:
        for i, memory in enumerate(self.memories):
            if addr >= memory.addr_range:
                addr -= memory.addr_range
            else:
                return i,addr
        raise IndexError("Out of bounds memory access")
        
    