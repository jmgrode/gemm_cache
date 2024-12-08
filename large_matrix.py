# large_matrix.py

from cpu import Cpu, CpuLatencies
from dram import Dram
from gemm_cache import GemmCache, GemmCacheLatencies
from program import Program
import numpy as np


MATRIX_DIM = 25
TILE_DIM = 5

dram_size = MATRIX_DIM * MATRIX_DIM * 5
dram = Dram(dram_size, 0, 100, 10)
gemm_cache_latencies = GemmCacheLatencies(matrix_dim=TILE_DIM)
gemm_cache = GemmCache(matrix_dim=TILE_DIM, num_matrices=4, addr_start=dram_size, gemm_cache_latencies=gemm_cache_latencies)
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
cache_addr_A = dram_size
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

# Create the program for matrix multiplication
program = Program(REGISTER_BYTES)

def move_from_dram_to_cache(program, dram_matrix, cache_matrix, size):
    program.add_immediate(1, 0, dram_matrix)   # r1 = addr_A (DRAM address for A)
    program.add_immediate(2, 0, cache_matrix)  # r2 = cache_addr_A (GemmCache address for A)
    program.add_immediate(3, 0, size)     # r3 = size of A
    program.move_memory(1, 2, 3)               # Move A from DRAM to GemmCache

def move_from_cache_to_dram(program, dram_matrix, cache_matrix, size):
    program.add_immediate(1, 0, cache_matrix)  # r1 = cache_addr_C (GemmCache address for C)
    program.add_immediate(2, 0, dram_matrix)   # r2 = addr_C (DRAM address for C)
    program.add_immediate(3, 0, size)     # r3 = size of C
    program.move_memory(1, 2, 3)               # Move C from GemmCache to DRAM

for row in range(0, MATRIX_DIM, TILE_DIM):
    for col in range(0, MATRIX_DIM, TILE_DIM):
        tile_height = TILE_DIM
        tile_width = TILE_DIM

        # Initialize C tile with D tile
        # D tile DRAM base:
        d_tile_dram_base = addr_D + row * MATRIX_DIM + col
        for r in range(tile_height):
            row_start = d_tile_dram_base + r * MATRIX_DIM
            move_from_dram_to_cache(program, row_start, cache_addr_C + r*TILE_DIM, TILE_DIM)

        # Now accumulate A*B into C
        for k in range(0, MATRIX_DIM, TILE_DIM):

            # If the k-tile doesn't fully cover TILE_DIM, we still place it in the cache padded with zeros
            # Move A tile: from A[row : row+tile_height, k : k+a_tile_width]
            a_tile_dram_base = addr_A + row * MATRIX_DIM + k
            for r in range(tile_height):
                row_start = a_tile_dram_base + r * MATRIX_DIM
                move_from_dram_to_cache(program, row_start, cache_addr_A  + r*TILE_DIM, TILE_DIM)

            # Move B tile: from B[k : k+b_tile_height, col : col+tile_width]
            b_tile_dram_base = addr_B + k * MATRIX_DIM + col
            for r in range(tile_height):
                row_start = b_tile_dram_base + r * MATRIX_DIM
                move_from_dram_to_cache(program, row_start, cache_addr_B  + r*TILE_DIM, TILE_DIM)

            # Perform D = A*B
            program.add_immediate(1, 0, cache_addr_D)  # r1 = D address in GemmCache
            program.add_immediate(2, 0, cache_addr_A)  # r2 = A address in GemmCache
            program.add_immediate(3, 0, cache_addr_B)  # r3 = B address in GemmCache
            program.matrix_multiply(1, 2, 3)

            # Perform the matrix add in GemmCache
            program.add_immediate(1, 0, cache_addr_C)  # r1 = cache_addr_C (GemmCache address for C)
            program.add_immediate(2, 0, cache_addr_D)  # r2 = cache_addr_D (GemmCache address for D)
            program.matrix_add(1, 2, 1)                # Add C and D, store result in C

        # After finishing accumulation over k, move C tile back to DRAM
        c_tile_dram_base = addr_C + row * MATRIX_DIM + col
        for r in range(TILE_DIM):
            row_start = c_tile_dram_base + r * MATRIX_DIM
            move_from_cache_to_dram(program, row_start, cache_addr_C  + r*TILE_DIM, TILE_DIM)
        
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
print(mat_C.shape)
print("Actual:\n", np.array(matrix_C))
print(np.array(matrix_C).shape)

if np.array_equal(mat_C, np.array(matrix_C)):
    print("Matmul is correct")
else:
    print("Matmul is not correct")


