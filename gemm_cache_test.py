from gemm_cache import GemmCache
from packet import Packet

if __name__ == "__main__":
    print("Testing GemmCache")

    # TODO: change test to assume 1B matrix elements instead of 2B matrix elements
    # TODO: remove dimensions

    # Initialize GemmCache
    MATRIX_SIZE = 72
    NUM_MATRICES = 3  # Number of matrices stored in cache
    READ_LATENCY = 5
    WRITE_LATENCY = 6
    MATMUL_LATENCY = 20
    MATADD_LATENCY = 15

    gemm_cache = GemmCache(
        matrix_size=MATRIX_SIZE,
        num_matrices=NUM_MATRICES,
        read_latency=READ_LATENCY,
        write_latency=WRITE_LATENCY,
        matmul_latency=MATMUL_LATENCY,
        matadd_latency=MATADD_LATENCY
    )


    # test write
    num_bytes = MATRIX_SIZE
    data = (1 << num_bytes * 8) - 1 # 8 bits per byte
    pkt_write = Packet(load=False, addr=0, size=num_bytes, data=data, latency=0)
    pkt_write_ret = GemmCache_obj.process_packet(pkt_write)
    assert(pkt_write_ret.load == False)
    assert(pkt_write_ret.addr == 0)
    assert(pkt_write_ret.size == num_bytes)
    assert(pkt_write_ret.data == data)
    assert(pkt_write_ret.latency == WRITE_LATENCY)

    # test read
    pkt_read = Packet(load=True, addr=0, size=num_bytes, data=None, latency = pkt_write_ret.latency)
    pkt_read_ret = GemmCache_obj.process_packet(pkt_read)
    assert(pkt_read_ret.load == True)
    assert(pkt_read_ret.addr == 0)
    assert(pkt_read_ret.size == num_bytes)
    assert(pkt_read_ret.data == data)
    assert(pkt_read_ret.latency == WRITE_LATENCY + READ_LATENCY) 

    # Test out-of-bounds access
    try:
        pkt_oob = Packet(load=True, addr=MATRIX_SIZE * NUM_MATRICES + 1, size=4, data=None, latency=0)
        gemm_cache.process_packet(pkt_oob)
    except AssertionError:
        print("Caught out-of-bounds access error as expected.")

    # test add
    pkt_write = Packet(load=False, addr=64, size=num_bytes, data=data, latency=pkt_read_ret.latency)
    pkt_write_ret = GemmCache_obj.process_packet(pkt_write)

    pkt_mat_add = Packet(multiply=False, matA_start=0, matB_start=64, matC_start = 64*2, dimA=[6, 6], dimB=[6, 6])
    pkt_mat_add_ret = GemmCache_obj.process_matrix_op_packet(pkt_mat_add)
    assert(pkt_mat_add_ret.latency == WRITE_LATENCY*2 + READ_LATENCY + MATADD_LATENCY)

    expected_data = None # TODO get the right expected data
    pkt_read = Packet(load=False, addr=64*2, size=num_bytes, data=data, latency=pkt_mat_add_ret.latency)
    pkt_read_ret = GemmCacheObj.process_packet(pkt_read)
    assert(pkt_read_ret.data == expected_data)

    # test multiply
    pkt_mat_mul = Packet(multiply=True, matA_start=0, matB_start=64, matC_start = 64*2, dimA=[3, 4], dimB=[4, 2])
    pkt_mat_mul_ret = GemmCache_obj.process_matrix_op_packet(pkt_mat_mul)
    assert(pkt_mat_mul_ret.latency == WRITE_LATENCY*2 + READ_LATENCY*2 + MATADD_LATENCY + MATMUL_LATENCY)

    expected_data = None # TODO get the right expected data
    num_bytes_output = 3 * 2 * 2 # 3 x 2 output dim and 2B per value
    pkt_read = Packet(load=False, addr=64*2, size=num_bytes_output, data=data, latency=pkt_mat_add_ret.latency)
    pkt_read_ret = GemmCacheObj.process_packet(pkt_read)
    assert(pkt_read_ret.data == expected_data)

    print("GemmCache Test Finished")
