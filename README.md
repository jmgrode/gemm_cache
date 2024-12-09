# **README: GeMM Simulation Framework**

## **Overview**
This project simulates a General Matrix Multiply (GeMM) operation using a custom-designed CPU, memory hierarchy, and instruction set architecture (ISA). The framework includes support for DRAM, a GemmCache for optimizing matrix operations, and a programmable CPU. It facilitates GeMM operations and provides a fully programmable environment for running custom programs that involve memory and arithmetic operations.

The framework is implemented in Python and is designed for educational and experimental purposes, enabling users to explore hardware design principles and low-level programming concepts.

---

## **Key Components**

### 1. **DRAM**
- **Class:** `Dram`
- **Purpose:** Simulates main memory, allowing storage and retrieval of data with configurable latencies and burst sizes.
- **Features:**
  - Load and store operations.
  - Configurable memory size, read latency, write latency, and burst size.
  - Out-of-bounds access handling.
  - Memory dump functionality for debugging.

---

### 2. **GemmCache**
- **Class:** `GemmCache`
- **Purpose:** Simulates a cache specifically designed for matrix operations like multiplication and addition.
- **Features:**
  - Optimized for matrix operations (`matrix_multiply`, `matrix_add`).
  - Configurable dimensions, number of matrices, and operation latencies.
  - Directly interfaces with DRAM.
  - Handles both scalar and matrix data through `Packet` and `MatrixPacket` objects.

---

### 3. **Cache**
- **Class:** `Cache`
- **Purpose:** General-purpose cache for scalar memory operations.
- **Features:**
  - Implements a simple block-based cache with eviction logic.
  - Supports both read and write operations.
  - Interfaces with DRAM for cache misses.
  - Eviction logic to ensure cache coherence.

---

### 4. **CPU**
- **Class:** `Cpu`
- **Purpose:** Simulates a programmable CPU capable of running a custom instruction set.
- **Features:**
  - Configurable number of registers and register size.
  - Direct interface with memory objects (e.g., DRAM, GemmCache).
  - Support for custom instructions, including arithmetic, bitwise, memory, and matrix operations.
  - Tracks program execution time (cycles).

---

### 5. **Program**
- **Class:** `Program`
- **Purpose:** Encapsulates instructions to be executed by the CPU.
- **Features:**
  - Customizable instruction set.
  - Labels and branching for flow control.
  - Support for memory, arithmetic, and matrix operations.
  - Converts instructions into a list for execution by the CPU.

---

### 6. **MemoryArray**
- **Class:** `MemoryArray`
- **Purpose:** Implements a contiguous byte-addressable memory for use in DRAM, caches, and matrix storage.
- **Features:**
  - Supports load, store, and delete operations.
  - Handles both scalar and multi-byte data.

---

### 7. **Packets**
- **Classes:** `Packet`, `MatrixPacket`
- **Purpose:** Encapsulate memory and matrix operation requests.
- **Features:**
  - Scalar memory access (`Packet`).
  - Matrix operation requests (`MatrixPacket`).

---

## **Instructions Overview**

### Supported Instructions
| **Instruction**      | **Purpose**                                  | **Example**                        |
|-----------------------|----------------------------------------------|------------------------------------|
| `load`               | Load data from memory to register            | `load(1, 0, 100)`                 |
| `store`              | Store register data to memory                | `store(1, 0, 100)`                |
| `move`               | Move immediate value to register             | `move(1, 42)`                     |
| `add`                | Add two registers and store result           | `add(3, 1, 2)`                    |
| `multiply`           | Multiply two registers and store result      | `multiply(3, 1, 2)`               |
| `matrix_multiply`    | Perform matrix multiplication in cache       | `matrix_multiply(1, 2, 3)`        |
| `matrix_add`         | Perform matrix addition in cache             | `matrix_add(1, 2, 3)`             |
| `halt`               | Stop program execution                       | `halt()`                          |

---

## **Usage Guide**

### Setting Up

1. **Dependencies**
   Ensure Python 3.7+ is installed along with `numpy` for matrix operations.

   pip install numpy

2. **Directory Structure**

   .
   ├── baseline.py
   ├── cache_test.py
   ├── cpu.py
   ├── dram.py
   ├── gemm_cache.py
   ├── gemm_cache_test.py
   ├── large_matrix.py
   ├── matrix.py
   ├── memory.py
   ├── memory_array.py
   ├── packet.py
   ├── program.py
   └── simple.py


3. **Run Examples**
Choose a file based on your use case. For example:
- `baseline.py` for initializing matrices and validating GeMM operations.
- `simple.py` for running a simple program to demonstrate basic CPU operations.
- `large_matrix.py` for testing operations on large matrices.
- `gemm_cache_test.py` or `cache_test.py` for unit testing specific components.

python baseline.py

---

### Sample Workflow: Matrix Multiply and Add

1. **Initialize DRAM**
Define matrices `A`, `B`, and `D` in any example script (e.g., `baseline.py`).

mat_A = np.random.randint(0, 2, size=(4, 4), dtype=np.int8)
mat_B = np.random.randint(0, 2, size=(4, 4), dtype=np.int8)
mat_D = np.random.randint(0, 2, size=(4, 4), dtype=np.int8)

2. **Create a Program**
Define operations to:
- Load matrices into GemmCache.
- Perform matrix multiplication and addition.
- Store the result back into DRAM.

program = Program(REGISTER_BYTES)
program.matrix_multiply(1, 2, 3)
program.matrix_add(1, 2, 1)
program.halt()

3. **Run the Program**
Execute the program using the CPU.

cpu.run_program(program)

4. **Validate Results**
Compare the computed result with the expected output.

assert np.array_equal(mat_C, np.array(matrix_C))

---

### Debugging Tools

- **`print_registers()`**: Prints the current state of CPU registers.
- **`print_memory()`**: Dumps the state of memory for debugging.
- **`Matrix Dumps`**: Verify the state of matrices in DRAM and GemmCache.

---

## **Extending the Framework**

1. **Add Instructions**
Define new instructions in `Cpu` and add their logic in `Program`.

2. **Optimize GemmCache**
Modify `GemmCache` for additional optimizations like tiling or multi-threading.

3. **Integrate More Complex Workloads**
Extend or create new example scripts for more sophisticated matrix operations.

---

## **Known Limitations**

- Assumes perfect alignment of matrix dimensions.
- Limited support for variable-sized cache blocks.
- Designed for single-threaded simulation only.

---

---

## **System Specifications and Heuristics**

### 1. **Cache**
- **Cache Size:** 32KB
- **Workload Sizes:** 
  - 4KB
  - 8KB
- **Note:** Currently, workloads larger than the GemmCache matrix size are not supported. This is a planned feature.

---

### 2. **Area Heuristics**
- **Components Considered:**
  - Number of adders.
  - Number of multipliers.
  - Number of flip-flops.
  - Number of comparators.
  - Number of sense amplifiers.
  - Other peripherals specific to scratchpad memory.
  - SRAM memory overhead based on the number of cells.

---

### 3. **GemmCache**
- **Area Heuristics:**
  - Each entry of the output matrix uses:
    - 1 8-bit adder.
    - 1 processing element, consisting of:
      - 1 8-bit multiplier.
      - 1 8-bit adder.
      - 8 flip-flops.
- **Matrix Multiply Latency:** 
  - \(2 \times (3d - 1)\) cycles, where \(d\) is the height of the square matrix.

---

## **Acknowledgments**
This project is a simplified educational tool for understanding low-level CPU and memory interactions, inspired by hardware simulation and system design principles.
