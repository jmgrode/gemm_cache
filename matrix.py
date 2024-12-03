from cpu import Cpu, CpuLatencies
from dram import Dram
from gemm_cache import GemmCache, Cache
from program import Program
import numpy as np

MATRIX_DIM = 4 # matrices are size MATRIX_DIM by MATRIX_DIM

dram = Dram(100000, 100, 10)
gemm_cache = GemmCache(matrix_dim=MATRIX_DIM, num_matrices=4, read_latency=10, write_latency=10, matmul_latency=5, matadd_latency=3)
cpu_latencies = CpuLatencies()
REGISTER_BYTES = 4
cpu = Cpu([dram, gemm_cache], 32, REGISTER_BYTES, 1, cpu_latencies)

# -----------------------------------------
# Initialize matrices in DRAM
# Example matrices:
# A = [[1, 2], [3, 4]]
# B = [[5, 6], [7, 8]]
# Expected C = [[19, 22], [43, 50]]


mat_A = np.random.randint(0, 2, size=(MATRIX_DIM, MATRIX_DIM), dtype=np.int8)
mat_B = np.random.randint(0, 2, size=(MATRIX_DIM, MATRIX_DIM), dtype=np.int8)
mat_D = np.random.randint(0, 2, size=(MATRIX_DIM, MATRIX_DIM), dtype=np.int8)
mat_C = np.add(np.matmul(mat_A, mat_B), mat_D)

rows_A, cols_A = mat_A.shape
rows_B, cols_B = mat_B.shape
rows_C, cols_C = mat_C.shape
rows_D, cols_D = mat_D.shape

matrix_A = mat_A.tolist()
matrix_B = mat_B.tolist()
matrix_D = mat_D.tolist()

# Initialize matrices A, B, and C
# matrix_A = [[1, 2], [3, 4]]  # Example 2x2 matrix
# matrix_B = [[5, 6], [7, 8]]  # Example 2x2 matrix
# matrix_C = [[0 for _ in range(cols_B)] for _ in range(rows_A)]  # Result matrix

# Addresses in DRAM
addr_A = 0
addr_B = addr_A + rows_A * cols_A # Each element is 1 byte
addr_C = addr_B + rows_B * cols_B
addr_D = addr_C + rows_C * cols_C

# GemmCache addresses (starting at 1000)
cache_addr_A = 100000
cache_addr_B = cache_addr_A + rows_A * cols_A
cache_addr_C = cache_addr_B + rows_B * cols_B
cache_addr_D = cache_addr_C + rows_C * cols_C

# Store matrices in DRAM
for i in range(rows_A):
    for j in range(cols_A):
        dram.set_value(addr_A + (i * cols_A + j), 1, matrix_A[i][j])

for i in range(rows_B):
    for j in range(cols_B):
        dram.set_value(addr_B + (i * cols_B + j), 1, matrix_B[i][j])

for i in range(rows_D):
    for j in range(cols_D):
        dram.set_value(addr_D + (i * cols_D + j), 1, matrix_D[i][j])

print("Matrix A in DRAM:")
for i in range(rows_A):
    for j in range(cols_A):
        value = dram.memory.load(addr_A + (i * cols_A + j), 1)
        print(f"A[{i}][{j}] = {value}")

print("Matrix B in DRAM:")
for i in range(rows_B):
    for j in range(cols_B):
        value = dram.memory.load(addr_B + (i * cols_B + j), 1)
        print(f"B[{i}][{j}] = {value}")

print("Matrix D in DRAM:")
for i in range(rows_D):
    for j in range(cols_D):
        value = dram.memory.load(addr_D + (i * cols_D + j), 1)
        print(f"D[{i}][{j}] = {value}")

# Create the program for matrix multiplication
program = Program(REGISTER_BYTES)

# Move matrices from DRAM to GemmCache
program.add_immediate(1, 0, addr_A)        # r1 = addr_A (DRAM address for A)
program.add_immediate(2, 0, cache_addr_A)  # r2 = cache_addr_A (GemmCache address for A)
program.add_immediate(3, 0, rows_A * cols_A)  # r3 = size of A
program.move_memory(1, 2, 3)               # Move A from DRAM to GemmCache

program.add_immediate(1, 0, addr_B)        # r1 = addr_B (DRAM address for B)
program.add_immediate(2, 0, cache_addr_B)  # r2 = cache_addr_B (GemmCache address for B)
program.add_immediate(3, 0, rows_B * cols_B)  # r3 = size of B
program.move_memory(1, 2, 3)               # Move B from DRAM to GemmCache

program.add_immediate(1, 0, addr_D)        # r1 = addr_D (DRAM address for D)
program.add_immediate(2, 0, cache_addr_D)  # r2 = cache_addr_D (GemmCache address for D)
program.add_immediate(3, 0, rows_D * cols_D)  # r3 = size of D
program.move_memory(1, 2, 3)               # Move D from DRAM to GemmCache

# Perform the matrix multiplication in GemmCache
program.add_immediate(1, 0, cache_addr_C)  # r1 = cache_addr_C (GemmCache address for C)
program.add_immediate(2, 0, cache_addr_A)  # r2 = cache_addr_A (GemmCache address for A)
program.add_immediate(3, 0, cache_addr_B)  # r3 = cache_addr_B (GemmCache address for B)
program.matrix_multiply(1, 2, 3)           # Multiply A and B, store result in C

# Perform the matrix add in GemmCache
program.add_immediate(1, 0, cache_addr_C)  # r1 = cache_addr_C (GemmCache address for C)
program.add_immediate(2, 0, cache_addr_D)  # r2 = cache_addr_D (GemmCache address for D)
program.matrix_add(1, 2, 1)                # Add C and D, store result in C

# Move result matrix C from GemmCache back to DRAM
program.add_immediate(1, 0, cache_addr_C)  # r1 = cache_addr_C (GemmCache address for C)
program.add_immediate(2, 0, addr_C)        # r2 = addr_C (DRAM address for C)
program.add_immediate(3, 0, rows_C * cols_C)  # r3 = size of C
program.move_memory(1, 2, 3)               # Move C from GemmCache to DRAM

program.halt()

# print("Program Instructions:")
# for instruction in program.instructions:
#     print(instruction)
# -----------------------------------------

cpu.run_program(program)

print("Resultant Matrix C:")

matrix_C = []
for i in range(rows_C):
    row = []
    for j in range(cols_C):
        value = dram.memory.load(addr_C + (i * cols_C + j), 1)
        row.append(value)
    matrix_C.append(row)

print("Expected:\n", mat_C)
print("Actual:\n", np.array(matrix_C))

if np.array_equal(mat_C, np.array(matrix_C)):
    print("Matmul is correct")
else:
    print("Matmul is not correct")

cpu.print_registers()

