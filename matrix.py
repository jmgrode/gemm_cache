from cpu import Cpu, CpuLatencies
from dram import Dram
from gemm_cache import GemmCache, Cache
from program import Program


#TODO: if/where to include fetch latency; probably just add as a fixed value to all cpu instructions
#TODO: write assembly programs for matrix multiplication with and without GeMMCache
#TODO: test everything

#TODO: scale up programs and validate programs

dram = Dram(1000, 100, 100) #TODO: should read and write latency be the same?
gemm_cache = GemmCache(matrix_dim=2, num_matrices=3, read_latency=10, write_latency=10, matmul_latency=5, matadd_latency=3)
cpu_latencies = CpuLatencies()
REGISTER_BYTES = 4
cpu = Cpu([dram, gemm_cache], 32, REGISTER_BYTES, 1, cpu_latencies)

#TODO: initialize dram with data?

# -----------------------------------------
# Initialize matrices in DRAM
# Example matrices:
# A = [[1, 2], [3, 4]]
# B = [[5, 6], [7, 8]]
# Expected C = [[19, 22], [43, 50]]

rows_A, cols_A = 2, 2  # Dimensions of matrix A
rows_B, cols_B = 2, 2  # Dimensions of matrix B
rows_C, cols_C = rows_A, cols_B  # Dimensions of matrix C (result)

# assert cols_A == rows_B, "Matrix multiplication requires cols_A == rows_B"

# Initialize matrices A, B, and C
matrix_A = [[1, 2], [3, 4]]  # Example 2x2 matrix
matrix_B = [[5, 6], [7, 8]]  # Example 2x2 matrix
# matrix_C = [[0 for _ in range(cols_B)] for _ in range(rows_A)]  # Result matrix

# Addresses in DRAM
addr_A = 0
addr_B = addr_A + rows_A * cols_A * 4  # Each element is 4 bytes
addr_C = addr_B + rows_B * cols_B * 4

# GemmCache addresses (starting at 1000)
cache_addr_A = 1000
cache_addr_B = cache_addr_A + rows_A * cols_A * 4
cache_addr_C = cache_addr_B + rows_B * cols_B * 4

# Store matrices in DRAM
for i in range(rows_A):
    for j in range(cols_A):
        dram.set_value(addr_A + (i * cols_A + j) * 4, 4, matrix_A[i][j])

for i in range(rows_B):
    for j in range(cols_B):
        dram.set_value(addr_B + (i * cols_B + j) * 4, 4, matrix_B[i][j])

print("Matrix A in DRAM:")
for i in range(rows_A):
    for j in range(cols_A):
        value = dram.memory.load(addr_A + (i * cols_A + j) * 4, 4)
        print(f"A[{i}][{j}] = {value}")

print("Matrix B in DRAM:")
for i in range(rows_B):
    for j in range(cols_B):
        value = dram.memory.load(addr_B + (i * cols_B + j) * 4, 4)
        print(f"B[{i}][{j}] = {value}")

# Create the program for matrix multiplication
program = Program(REGISTER_BYTES)

# Move matrices from DRAM to GemmCache
program.add_immediate(1, 0, addr_A)        # r1 = addr_A (DRAM address for A)
program.add_immediate(2, 0, cache_addr_A)  # r2 = cache_addr_A (GemmCache address for A)
program.add_immediate(3, 0, rows_A * cols_A * 4)  # r3 = size of A
program.move_memory(1, 2, 3)               # Move A from DRAM to GemmCache

program.add_immediate(1, 0, addr_B)        # r1 = addr_B (DRAM address for B)
program.add_immediate(2, 0, cache_addr_B)  # r2 = cache_addr_B (GemmCache address for B)
program.add_immediate(3, 0, rows_B * cols_B * 4)  # r3 = size of B
program.move_memory(1, 2, 3)               # Move B from DRAM to GemmCache

# Perform the matrix multiplication in GemmCache
program.add_immediate(1, 0, cache_addr_C)  # r1 = cache_addr_C (GemmCache address for C)
program.add_immediate(2, 0, cache_addr_A)  # r2 = cache_addr_A (GemmCache address for A)
program.add_immediate(3, 0, cache_addr_B)  # r3 = cache_addr_B (GemmCache address for B)
program.matrix_multiply(1, 2, 3)           # Multiply A and B, store result in C

# Move result matrix C from GemmCache back to DRAM
program.add_immediate(1, 0, cache_addr_C)  # r1 = cache_addr_C (GemmCache address for C)
program.add_immediate(2, 0, addr_C)        # r2 = addr_C (DRAM address for C)
program.add_immediate(3, 0, rows_C * cols_C * 4)  # r3 = size of C
program.move_memory(1, 2, 3)               # Move C from GemmCache to DRAM

program.halt()

# print("Program Instructions:")
# for instruction in program.instructions:
#     print(instruction)
# -----------------------------------------

cpu.run_program(program)

print("Resultant Matrix C:")
for i in range(rows_C):
    row = []
    for j in range(cols_C):
        value = dram.memory.load(addr_C + (i * cols_C + j) * 4, 4)
        row.append(value)
    print(row)

cpu.print_registers()