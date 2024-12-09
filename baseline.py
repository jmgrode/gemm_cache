# baseline.py

from cpu import Cpu, CpuLatencies
from dram import Dram
from gemm_cache import Cache
from program import Program
import numpy as np

MATRIX_DIM = 4 # matrices are size MATRIX_DIM by MATRIX_DIM

dram = Dram(32768, 0, 100, 10)
# TODO: Either make Cache support variable size or fix it to a number
cache = Cache(256, 32768, 8, 1, 1, dram) #TODO: change dram stuff arguments
cpu_latencies = CpuLatencies()
REGISTER_BYTES = 4
cpu = Cpu([cache], 32, REGISTER_BYTES, -1, cpu_latencies)

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

# Addresses in DRAM
addr_A = 0
addr_B = addr_A + rows_A * cols_A  # Each element is 4 bytes
addr_C = addr_B + rows_B * cols_B
addr_D = addr_C + rows_C * cols_C

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

# Create the program for GeMM
program = Program(REGISTER_BYTES)

# Load and compute matrix multiply
for i in range(rows_A):  # Iterate over rows of A
    for j in range(cols_B):  # Iterate over columns of B
        # Initialize C[i][j] to 0
        program.add_immediate(5, 0, 0)  # r5 = 0

        for k in range(cols_A):  # Iterate over shared dimension
            # Load A[i][k] and B[k][j]
            program.load_byte(2, 1, addr_A + (i * cols_A + k))  # r2 = A[i][k]
            program.load_byte(3, 1, addr_B + (k * cols_B + j))  # r3 = B[k][j]

            # Multiply A[i][k] * B[k][j]
            program.multiply(4, 2, 3)  # r4 = r2 * r3

            # Add product to C[i][j]
            program.add(5, 5, 4)  # r5 = r5 + r4

        # Store result back to C[i][j]
        program.store_byte(5, 1, addr_C + (i * cols_B + j))

# Load and compute matrix add
for i in range(rows_C):  # Iterate over rows of C
    for j in range(cols_C):  # Iterate over columns of C
        # Load C[i][j] and D[i][j]
        program.load_byte(2, 1, addr_C + (i * cols_C + j))  # r2 = C[i][j]
        program.load_byte(3, 1, addr_D + (i * cols_D + j))  # r3 = D[i][j]

        # Add C[i][j] + D[i][j]
        program.add(4, 2, 3)  # r4 = r2 + r3

        # Store result back to C[i][j]
        program.store_byte(4, 1, addr_C + (i * cols_C + j))

program.halt()


cpu.run_program(program)

cache.evict_cache() # for syncing to memory

matrix_C = []
for i in range(rows_C):
    row = []
    for j in range(cols_C):
        value = dram.memory.load(addr_C + (i * cols_C + j), 1)
        if value > 127:
            value -= 256
        row.append(np.int8(value))
    matrix_C.append(row)

print("Expected:\n", mat_C)
print("Output:\n", np.array(matrix_C))

if np.array_equal(mat_C, np.array(matrix_C)):
    print("GeMM is correct")
else:
    print("GeMM is not correct")

# cpu.print_registers()
# for addr,data in cache.cache.array.items():
#     dram.memory[addr] = data
dram.print(0)
#cpu.print_memory()
