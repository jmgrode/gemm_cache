# simple.py

from cpu import Cpu, CpuLatencies
from dram import Dram
from gemm_cache import GemmCache, Cache
from program import Program

dram = Dram(32768, 0, 100, 10)
cache = Cache(1024, 32768, 8, 1, 1, dram)
cpu_latencies = CpuLatencies()
REGISTER_BYTES = 4
cpu = Cpu([cache], 32, REGISTER_BYTES, -1, cpu_latencies)

program = Program(REGISTER_BYTES)

program.move(1, 1) # r1 = 1
program.move(2, 2) # r2 = 2
program.add(3, 1, 2) # r3 = 3
program.halt()

cpu.run_program(program)
cpu.print_registers()
