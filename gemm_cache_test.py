# gemm_cache_test.py

from gemm_cache import GemmCache
from packet import Packet, MatrixPacket
import numpy as np

def integer_to_array(integer, rows, cols, dtype=np.uint8):
    total_elements = rows * cols
    flat_array = []
    for i in range(total_elements):
        # Extract 8 bits at a time
        value = (integer >> (i * 8)) & 0xFF
        flat_array.append(value)
    # Reshape the flat array into the original 2D shape
    return np.array(flat_array, dtype=dtype).reshape(rows, cols)

def array_to_integer(array):
    total_integer = 0
    for i, value in enumerate(array):
        total_integer |= int(value) << (i * 8)
    return total_integer

if __name__ == "__main__":
    print("Testing GemmCache")

    # Initialize GemmCache
    NUM_MATRICES = 3  # Number of matrices stored in cache
    READ_LATENCY = 5
    WRITE_LATENCY = 6
    MATMUL_LATENCY = 20
    MATADD_LATENCY = 15
    MATRIX_DIM = 3
    MATRIX_SIZE = MATRIX_DIM * MATRIX_DIM

    gemm_cache = GemmCache(
        matrix_dim=MATRIX_DIM,
        num_matrices=NUM_MATRICES,
        read_latency=READ_LATENCY,
        write_latency=WRITE_LATENCY,
        matmul_latency=MATMUL_LATENCY,
        matadd_latency=MATADD_LATENCY
    )

    matA = np.random.randint(0, 2, size=(MATRIX_DIM, MATRIX_DIM), dtype=np.uint8)
    matB = np.random.randint(0, 2, size=(MATRIX_DIM, MATRIX_DIM), dtype=np.uint8)
    matA_flat = array_to_integer(matA.flatten(order='C'))  # 'C' specifies row-major order
    matB_flat = array_to_integer(matB.flatten(order='C'))

    # test write
    pkt_write = Packet(load=False, addr=0, size=MATRIX_SIZE, data=matA_flat, latency=0)
    pkt_write_ret = gemm_cache.process_packet(pkt_write)
    assert(pkt_write_ret.load == False)
    assert(pkt_write_ret.addr == 0)
    assert(pkt_write_ret.size == MATRIX_SIZE)
    assert(pkt_write_ret.data == matA_flat)
    assert(pkt_write_ret.latency == WRITE_LATENCY)

    # test read
    pkt_read = Packet(load=True, addr=0, size=MATRIX_SIZE, data=None, latency = pkt_write_ret.latency)
    pkt_read_ret = gemm_cache.process_packet(pkt_read)
    assert(pkt_read_ret.load == True)
    assert(pkt_read_ret.addr == 0)
    assert(pkt_read_ret.size == MATRIX_SIZE)
    assert(pkt_read_ret.data == matA_flat)
    assert(pkt_read_ret.latency == WRITE_LATENCY + READ_LATENCY) 

    # test add in place
    pkt_write = Packet(load=False, addr=MATRIX_SIZE, size=MATRIX_SIZE, data=matB_flat, latency=pkt_read_ret.latency)
    pkt_write_ret = gemm_cache.process_packet(pkt_write)

    pkt_mat_add = MatrixPacket(multiply=False, matA_start=0, matB_start=MATRIX_SIZE, matC_start = MATRIX_SIZE, latency=pkt_write_ret.latency)
    pkt_mat_add_ret = gemm_cache.process_matrix_op_packet(pkt_mat_add)
    assert(pkt_mat_add_ret.latency == WRITE_LATENCY*2 + READ_LATENCY + MATADD_LATENCY)

    expected_mat = np.add(matA, matB, dtype=np.uint8)
    expected_mat_flat = array_to_integer(expected_mat.flatten(order='C'))
    pkt_read = Packet(load=True, addr=MATRIX_SIZE, size=MATRIX_SIZE, data=None, latency=pkt_mat_add_ret.latency)
    pkt_read_ret = gemm_cache.process_packet(pkt_read)
    assert(pkt_read_ret.data == expected_mat_flat)

    # # test add
    # pkt_write = Packet(load=False, addr=MATRIX_SIZE, size=MATRIX_SIZE, data=matB_flat, latency=pkt_read_ret.latency)
    # pkt_write_ret = gemm_cache.process_packet(pkt_write)

    # pkt_mat_add = MatrixPacket(multiply=False, matA_start=0, matB_start=MATRIX_SIZE, matC_start = MATRIX_SIZE*2, latency=pkt_write_ret.latency)
    # pkt_mat_add_ret = gemm_cache.process_matrix_op_packet(pkt_mat_add)
    # assert(pkt_mat_add_ret.latency == WRITE_LATENCY*2 + READ_LATENCY + MATADD_LATENCY)

    # expected_mat = np.add(matA, matB, dtype=np.uint8)
    # expected_mat_flat = array_to_integer(expected_mat.flatten(order='C'))
    # pkt_read = Packet(load=True, addr=MATRIX_SIZE*2, size=MATRIX_SIZE, data=None, latency=pkt_mat_add_ret.latency)
    # pkt_read_ret = gemm_cache.process_packet(pkt_read)
    # assert(pkt_read_ret.data == expected_mat_flat)

    # # test multiply
    # pkt_mat_mul = MatrixPacket(multiply=True, matA_start=0, matB_start=MATRIX_SIZE, matC_start = MATRIX_SIZE*2, latency=pkt_read_ret.latency)
    # pkt_mat_mul_ret = gemm_cache.process_matrix_op_packet(pkt_mat_mul)
    # assert(pkt_mat_mul_ret.latency == WRITE_LATENCY*2 + READ_LATENCY*2 + MATADD_LATENCY + MATMUL_LATENCY)

    # expected_mat = np.matmul(matA, matB)
    # expected_mat_flat = array_to_integer(expected_mat.flatten(order='C'))
    # pkt_read = Packet(load=True, addr=MATRIX_SIZE*2, size=MATRIX_SIZE, data=None, latency=pkt_mat_mul_ret.latency)
    # pkt_read_ret = gemm_cache.process_packet(pkt_read)
    # assert(pkt_read_ret.data == expected_mat_flat)

    print("GemmCache Test Finished")
