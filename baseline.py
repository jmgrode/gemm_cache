from cpu import Cpu, CpuLatencies
from dram import Dram
from gemm_cache import GemmCache, Cache
from program import Program

dram = Dram(32768, 100, 10)
cache = Cache(1024, 32768, 8, 1, 1, dram) #TODO: change dram stuff arguments
cpu_latencies = CpuLatencies()
REGISTER_BYTES = 4
cpu = Cpu([cache], 32, REGISTER_BYTES, -1, cpu_latencies)

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
matrix_C = [[0 for _ in range(cols_B)] for _ in range(rows_A)]  # Result matrix

# Addresses in DRAM
addr_A = 0
addr_B = addr_A + rows_A * cols_A * 4  # Each element is 4 bytes
addr_C = addr_B + rows_B * cols_B * 4

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

# Load and compute
for i in range(rows_A):  # Iterate over rows of A
    for j in range(cols_B):  # Iterate over columns of B
        # Initialize C[i][j] to 0
        program.add_immediate(0, 0, 0)  # r0 = 0
        program.store(0, 1, addr_C + (i * cols_B + j) * 4)  # Store r0 -> C[i][j]

        for k in range(cols_A):  # Iterate over shared dimension
            # Load A[i][k] and B[k][j]
            program.load(2, 1, addr_A + (i * cols_A + k) * 4)  # r2 = A[i][k]
            program.load(3, 1, addr_B + (k * cols_B + j) * 4)  # r3 = B[k][j]

            # Multiply A[i][k] * B[k][j]
            program.multiply(4, 2, 3)  # r4 = r2 * r3

            # Load C[i][j]
            program.load(5, 1, addr_C + (i * cols_B + j) * 4)  # r5 = C[i][j]

            # Add product to C[i][j]
            program.add(5, 5, 4)  # r5 = r5 + r4

            # Store result back to C[i][j]
            program.store(5, 1, addr_C + (i * cols_B + j) * 4)

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

"""
Below is an example of how you might implement matrix multiplication using x86-64 assembly. This code assumes that:

1. Matrices are stored in row-major order.
2. The sizes of matrices are passed as parameters (e.g., `rows_A`, `cols_A` for matrix A, and `cols_B` for matrix B).
3. The result matrix `C` has dimensions `rows_A x cols_B`.

---
section .data
    ; Matrices are assumed to be initialized in C or passed as parameters.

section .text
    global matrix_multiply

; Function prototype:
; void matrix_multiply(double* A, double* B, double* C, int rows_A, int cols_A, int cols_B)
matrix_multiply:
    push rbp                ; Save base pointer
    mov rbp, rsp            ; Set base pointer

    mov rdi, [rbp + 16]     ; A (pointer)
    mov rsi, [rbp + 24]     ; B (pointer)
    mov rdx, [rbp + 32]     ; C (pointer)
    mov rcx, [rbp + 40]     ; rows_A
    mov r8,  [rbp + 48]     ; cols_A
    mov r9,  [rbp + 56]     ; cols_B

    xor r10, r10            ; i = 0
.outer_loop:                 ; Outer loop over rows of A
    cmp r10, rcx            ; if i >= rows_A, exit
    jge .done

    xor r11, r11            ; j = 0
.inner_loop:                 ; Inner loop over cols of B
    cmp r11, r9             ; if j >= cols_B, exit
    jge .next_row

    xor r12, r12            ; k = 0
    movq xmm0, qword [rdx + r10 * r9 * 8 + r11 * 8] ; C[i][j] = 0
    pxor xmm0, xmm0         ; Clear xmm0

.k_loop:                    ; Loop over cols of A / rows of B
    cmp r12, r8             ; if k >= cols_A, exit
    jge .store_result

    ; Load A[i][k]
    mov r13, r10            ; r13 = i
    imul r13, r8            ; r13 = i * cols_A
    add r13, r12            ; r13 = i * cols_A + k
    movq xmm1, qword [rdi + r13 * 8]

    ; Load B[k][j]
    mov r14, r12            ; r14 = k
    imul r14, r9            ; r14 = k * cols_B
    add r14, r11            ; r14 = k * cols_B + j
    movq xmm2, qword [rsi + r14 * 8]

    ; Multiply A[i][k] * B[k][j]
    mulsd xmm1, xmm2

    ; Accumulate into xmm0
    addsd xmm0, xmm1

    inc r12                 ; k++
    jmp .k_loop

.store_result:
    ; Store result in C[i][j]
    mov r15, r10            ; r15 = i
    imul r15, r9            ; r15 = i * cols_B
    add r15, r11            ; r15 = i * cols_B + j
    movq qword [rdx + r15 * 8], xmm0

    inc r11                 ; j++
    jmp .inner_loop

.next_row:
    inc r10                 ; i++
    jmp .outer_loop

.done:
    pop rbp
    ret
---

### Explanation:
1. **Registers:**
   - `rdi`, `rsi`, and `rdx` hold pointers to matrices A, B, and C.
   - `rcx`, `r8`, and `r9` store dimensions `rows_A`, `cols_A`, and `cols_B`.

2. **Loops:**
   - **Outer loop (`i`):** Iterates over rows of matrix A.
   - **Inner loop (`j`):** Iterates over columns of matrix B.
   - **K loop (`k`):** Iterates through the shared dimension to compute the dot product for C[i][j].

3. **Math and Storage:**
   - Each element of C is computed as the dot product of row `i` of A and column `j` of B.
   - Accumulated results are stored in `C[i][j]`.

### Usage:
This function assumes double-precision floating-point values for the matrix elements. To call this function, you need to set up the arguments in the right registers or stack locations as per the x86-64 calling convention.

For optimization, this code can be improved using SIMD operations (e.g., AVX instructions) for better performance on larger matrices.

"""