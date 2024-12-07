# gemm_cache

Cache Size: 32KB
Workload Sizes(size of matrices for matmul and matadd): 4KB, 8KB
# TODO: enable workloads bigger than gemm_cache matrix size
Area Heuristics: Number of adders, multipliers, flip flops, comparators, sense amps, other peripherals specific to scratchpad mem, SRAM memory overhead based on number of cells?
GemmCache Area Heuristics: 1 8-bit adder and 1 processing element (1 8-bit multiplier and 1 8-bit adder, 8 flip flops) for each entry of the output matrix
GemmCache Matmul Latency: 2(3d-1) cycles where d is height of the square matrix

## Components Overview

### CPU
CPU accepts multiple parameters:
- Configurable number of registers and register sizes
- Basic arithmetic operations (add, multiply)
- Memory operations (load, store)
- Branch and jump instructions
- Logical operations (bitwise operations, shifts)
- Matrix operations with GemmCache

```python
# CPU initialization
cpu_latencies = CpuLatencies()  # Define operation latencies
cpu = Cpu(
    memories=[dram, gemm_cache],  # List of memory components
    num_registers=32,             # Number of registers
    register_bytes=4,             # Size of each register
    gemm_port=1,                 # Port for GemmCache (-1 if not used)
    cpu_latencies=cpu_latencies
)
```

### DRAM
Main memory with configurable size and latencies:
```python
dram = Dram(
    size=32768,           # Total memory size
    read_latency=100,     # Read latency cycles
    write_latency=10,     # Write latency cycles
    burst_size=64        # Optional: Burst size for transfers
)
```

### Traditional Cache
Direct-mapped cache with DRAM backing:
```python
cache = Cache(
    size=256,            # Cache size in bytes
    addr_range=32768,    # Address range covered
    block_size=8,        # Cache block size
    read_latency=1,      # Cache read latency
    write_latency=1,     # Cache write latency
    dram=dram           # Backing DRAM
)
```

### GemmCache
GeMM cache for matrix operations:
```python
gemm_cache = GemmCache(
    matrix_dim=4,        # Matrix dimension (NxN)
    num_matrices=4,      # Number of matrices that can be stored
    read_latency=10,     # Read latency cycles
    write_latency=10,    # Write latency cycles
    matmul_latency=5,    # Matrix multiply latency
    matadd_latency=3,    # Matrix add latency
    bytes_per_element=1  # Size of each matrix element
)
```

## Creating Programs

Use the Program class to create instruction sequences:

```python
program = Program(register_bytes=4)

# Arithmetic Operations
program.add(dest_reg, src_reg1, src_reg2)
program.add_immediate(dest_reg, src_reg, immediate)
program.multiply(dest_reg, src_reg1, src_reg2)

# Memory Operations
program.load(dest_reg, addr_reg, immediate)
program.store(src_reg, addr_reg, immediate)
program.move_memory(src_addr_reg, dest_addr_reg, size_reg)
program.move(dest_reg, immediate)

# Control Flow
program.branch_if(cond_reg, immediate)     # Branch if cond_reg != 0
program.jump(dest_reg)                     # Jump to address in register

# Logical Operations
program.bitwise_or(dest_reg, src_reg1, src_reg2)
program.bitwise_and(dest_reg, src_reg1, src_reg2)
program.bitwise_xor(dest_reg, src_reg1, src_reg2)
program.bitwise_nor(dest_reg, src_reg1, src_reg2)
program.bitwise_not(dest_reg, src_reg)
program.logical_shift_left(dest_reg, value_reg, shift_size)
program.logical_shift_right(dest_reg, value_reg, shift_size)

# Matrix Operations (GemmCache)
program.matrix_multiply(dest_addr_reg, src1_addr_reg, src2_addr_reg)
program.matrix_add(dest_addr_reg, src1_addr_reg, src2_addr_reg)

program.halt()  # End program
```

## Example Programs

### 1. Matrix Multiply using Traditional Cache
```python
program = Program(REGISTER_BYTES=1)

# Matrix multiplication loop
for i in range(rows_A):
    for j in range(cols_B):
        program.add_immediate(0, 0, 0)  # Clear accumulator
        for k in range(cols_A):
            # Load matrix elements
            program.load(2, 1, addr_A + (i * cols_A + k))
            program.load(3, 1, addr_B + (k * cols_B + j))
            # Multiply and accumulate
            program.multiply(4, 2, 3)
            program.add(0, 0, 4)
        # Store result
        program.store(0, 1, addr_C + (i * cols_B + j))

program.halt()
```

### 2. Matrix Operations using GemmCache
```python
program = Program(REGISTER_BYTES=4)

# Load matrices into GemmCache
program.move_memory(dram_addr_a, cache_addr_a, matrix_size)
program.move_memory(dram_addr_b, cache_addr_b, matrix_size)

# Perform matrix multiply
program.matrix_multiply(cache_addr_c, cache_addr_a, cache_addr_b)

# Store result back to DRAM
program.move_memory(cache_addr_c, dram_addr_c, matrix_size)

program.halt()
```

## Debugging

```python
# CPU State
cpu.print_registers()          # Show register contents
cpu.print_memory()            # Show all memory contents

# Memory Contents
dram.print(0)                # Print DRAM from address 0
cache.print(0)              # Print cache contents
gemm_cache.print_memory(0)  # Print GemmCache contents

# Cache Management
cache.evict_cache()         # Write cache contents to DRAM
```

## Performance Monitoring

The simulator tracks cycles for:
- Individual instructions (defined in CpuLatencies)
- Memory operations (read/write latencies)
- Matrix operations (matmul/matadd latencies)
- Total program execution time

```python
# Run program and get performance
cpu.run_program(program)  # Prints final cycle count
```