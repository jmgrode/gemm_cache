# large_matrix.py

from cpu import Cpu, CpuLatencies
from dram import Dram
from gemm_cache import GemmCache, Cache
from program import Program
import numpy as np


MATRIX_DIM = 258
TILE_DIM = 50

dram = Dram(100000, 100, 10)
gemm_cache = GemmCache(matrix_dim=TILE_DIM, num_matrices=4, read_latency=10, write_latency=10, matmul_latency=5, matadd_latency=3)
cpu_latencies = CpuLatencies()
REGISTER_BYTES = 4
cpu = Cpu([dram, gemm_cache], 32, REGISTER_BYTES, 1, cpu_latencies)

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

# Addresses in DRAM
addr_A = 0
addr_B = addr_A + MATRIX_DIM * MATRIX_DIM # Each element is 1 byte
addr_C = addr_B + MATRIX_DIM * MATRIX_DIM
addr_D = addr_C + MATRIX_DIM * MATRIX_DIM

# GemmCache addresses
cache_addr_A = 100000
cache_addr_B = cache_addr_A + TILE_DIM * TILE_DIM
cache_addr_C = cache_addr_B + TILE_DIM * TILE_DIM
cache_addr_D = cache_addr_C + TILE_DIM * TILE_DIM

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

for row in range(0, MATRIX_DIM, TILE_DIM):
    for col in range(0, MATRIX_DIM, TILE_DIM):
        tile_height = min(TILE_DIM, MATRIX_DIM - row)
        tile_width = min(TILE_DIM, MATRIX_DIM - col)

        tile_size = tile_height * tile_width

        # fill cache matrices with 0s if tile size does not fit all of the available space

        for i in range(0, MATRIX_DIM, TILE_DIM):

            # perhaps calculate new DRAM addresses for the tiles

            # Move matrices from DRAM to GemmCache # TODO: FIX ADDRESSES MAYBE
            program.add_immediate(1, 0, addr_A)        # r1 = addr_A (DRAM address for A)
            program.add_immediate(2, 0, cache_addr_A)  # r2 = cache_addr_A (GemmCache address for A)
            program.add_immediate(3, 0, tile_size)  # r3 = size of A
            program.move_memory(1, 2, 3)               # Move A from DRAM to GemmCache

            program.add_immediate(1, 0, addr_B)        # r1 = addr_B (DRAM address for B)
            program.add_immediate(2, 0, cache_addr_B)  # r2 = cache_addr_B (GemmCache address for B)
            program.add_immediate(3, 0, tile_size)  # r3 = size of B
            program.move_memory(1, 2, 3)               # Move B from DRAM to GemmCache

            program.add_immediate(1, 0, addr_D)        # r1 = addr_D (DRAM address for D)
            program.add_immediate(2, 0, cache_addr_D)  # r2 = cache_addr_D (GemmCache address for D)
            program.add_immediate(3, 0, tile_size)  # r3 = size of D
            program.move_memory(1, 2, 3)               # Move D from DRAM to GemmCache

            # Perform the matrix multiplication in GemmCache
            program.add_immediate(1, 0, cache_addr_C)  # r1 = cache_addr_C (GemmCache address for C)
            program.add_immediate(2, 0, cache_addr_A)  # r2 = cache_addr_A (GemmCache address for A)
            program.add_immediate(3, 0, cache_addr_B)  # r3 = cache_addr_B (GemmCache address for B)
            program.matrix_multiply(1, 2, 3)           # Multiply A and B, store result in C

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

