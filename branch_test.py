from cpu import Cpu, CpuLatencies
from dram import Dram
from gemm_cache import Cache
from program import Program
import numpy as np

MATRIX_DIM = 4 # matrices are size MATRIX_DIM by MATRIX_DIM

dram = Dram(32768, 100, 10)
# TODO: Either make Cache support variable size or fix it to a number
cache = Cache(256, 32768, 8, 1, 1, dram) #TODO: change dram stuff arguments
cpu_latencies = CpuLatencies()
REGISTER_BYTES = 4
cpu = Cpu([cache], 32, REGISTER_BYTES, -1, cpu_latencies)

program = Program(REGISTER_BYTES)

# Loops adding 1 to r2 until it equals 4, then halts
program.move(4, 4)
program.insert_label("loop")
program.bitwise_and(1, 4, 2)
program.label_branch_if(1, "done")
program.add_immediate(2, 2, 1)
program.label_jump(31, "loop")
program.insert_label("done")
program.halt()

cpu.run_program(program)

cpu.print_registers()
