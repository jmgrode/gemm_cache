from gemm_cache import GemmCache
from packet import Packet

if __name__ == "__main__":
    print("Testing GemmCache")

    # Initialize GemmCache
    MATRIX_SIZE = 4  # Example size of a matrix (4x4)
    NUM_MATRICES = 2  # Number of matrices stored in cache
    READ_LATENCY = 5
    WRITE_LATENCY = 6
    MATMUL_LATENCY = 20
    MATADD_LATENCY = 15

    gemm_cache = GemmCache(
        matrix_size=MATRIX_SIZE,
        num_matrices=NUM_MATRICES,
        ports=[],  # Providing an empty list for ports
        read_latency=READ_LATENCY,
        write_latency=WRITE_LATENCY,
        matmul_latency=MATMUL_LATENCY,
        matadd_latency=MATADD_LATENCY
    )


    # Test write
    data = 0x12345678  # Example data to write
    addr = 0
    pkt_write = Packet(load=False, addr=addr, size=4, data=data, latency=0)
    pkt_write_ret = gemm_cache.process_packet(pkt_write)
    assert pkt_write_ret.load == False
    assert pkt_write_ret.addr == addr
    assert pkt_write_ret.size == 0
    assert pkt_write_ret.data == None
    assert pkt_write_ret.latency == WRITE_LATENCY * 4

    # Test read
    pkt_read = Packet(load=True, addr=addr, size=4, data=None, latency=0)
    pkt_read_ret = gemm_cache.process_packet(pkt_read)
    assert pkt_read_ret.load == True
    assert pkt_read_ret.addr == addr
    assert pkt_read_ret.size == 4
    assert pkt_read_ret.data == data
    assert pkt_read_ret.latency == READ_LATENCY * 4

    # Test out-of-bounds access
    try:
        pkt_oob = Packet(load=True, addr=MATRIX_SIZE * NUM_MATRICES + 1, size=4, data=None, latency=0)
        gemm_cache.process_packet(pkt_oob)
    except AssertionError:
        print("Caught out-of-bounds access error as expected.")

    # Placeholder for matrix operations
    # Add tests for `matrix_multiply` and `matrix_add` once implemented
    try:
        gemm_cache.matrix_multiply()
    except NotImplementedError:
        print("Matrix multiply not implemented yet.")

    try:
        gemm_cache.matrix_add()
    except NotImplementedError:
        print("Matrix add not implemented yet.")

    print("GemmCache Test Finished")
