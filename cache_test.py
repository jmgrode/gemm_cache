from gemm_cache import Cache
from packet import Packet
from dram import Dram

if __name__ == "__main__":
    print("Testing Cache")

    CACHE_SIZE = 256 # bytes
    CACHE_ADDR_RANGE = 4096 # bytes
    CACHE_BLOCK_SIZE = 8
    CACHE_READ_LATENCY = 1
    CACHE_WRITE_LATENCY = 1
    CACHE_DRAM = Dram(4096, 100, 10)

    cache = Cache(CACHE_SIZE, CACHE_ADDR_RANGE, CACHE_BLOCK_SIZE, CACHE_READ_LATENCY, CACHE_WRITE_LATENCY, CACHE_DRAM)

    # test_store = Packet(load=False, addr=0x0100, size=8, data=0x000000FF, latency=1)
    # ret_pkt = cache.process_packet(test_store)
    # assert(ret_pkt.load == False)
    # assert(ret_pkt.addr == 0x100)
    # assert(ret_pkt.size == 8)
    # assert(ret_pkt.data == 0xFF)

    # test_load = Packet(load=True, addr=0x0100, size=8, data=0x00000000, latency=1)
    # ret_pkt = cache.process_packet(test_load)

    # test_store = Packet(load=False, addr=0x0900, size=8, data=0x00000088, latency=1)
    # ret_pkt = cache.process_packet(test_store)
    # assert(ret_pkt.load == False)
    # assert(ret_pkt.addr == 0x0900)
    # assert(ret_pkt.size == 8)
    # assert(ret_pkt.data == 0x88)

    # test_load = Packet(load=True, addr=0x0900, size=8, data=0x00000000, latency=1)
    # ret_pkt = cache.process_packet(test_load)
    # assert(ret_pkt.data == 0x88)

    # test_load = Packet(load=True, addr=0x0100, size=8, data=0x00000000, latency=1)
    # ret_pkt = cache.process_packet(test_load)
    # assert(ret_pkt.data == 0xFF)

    # test_load = Packet(load=True, addr=0x0900, size=8, data=0x00000000, latency=1)
    # ret_pkt = cache.process_packet(test_load)
    # assert(ret_pkt.data == 0x88)

    # test_load = Packet(load=True, addr=0x0100, size=8, data=0x00000000, latency=1)
    # ret_pkt = cache.process_packet(test_load)
    # assert(ret_pkt.data == 0xFF)

    # test_load = Packet(load=True, addr=0x0900, size=8, data=0x00000000, latency=1)
    # ret_pkt = cache.process_packet(test_load)
    # assert(ret_pkt.data == 0x88)

    # test_load = Packet(load=True, addr=0x0100, size=8, data=0x00000000, latency=1)
    # ret_pkt = cache.process_packet(test_load)
    # assert(ret_pkt.data == 0xFF)

    # test_load = Packet(load=True, addr=0x0900, size=8, data=0x00000000, latency=1)
    # ret_pkt = cache.process_packet(test_load)
    # assert(ret_pkt.data == 0x88)

    # test_load = Packet(load=True, addr=0x0100, size=8, data=0x00000000, latency=1)
    # ret_pkt = cache.process_packet(test_load)
    # assert(ret_pkt.data == 0xFF)

    for i in range(256):
        test_store = Packet(load=False, addr=0x0000 + (i*4), size=1, data=i, latency=1)
        ret_pkt = cache.process_packet(test_store)

    for i in range(256):    
        test_load = Packet(load=True, addr=0x0000 + (i*4), size=1, data=i, latency=1)
        ret_pkt = cache.process_packet(test_load)
        print(ret_pkt.data)
        assert(ret_pkt.data == i)

    #cache.print(0)
    cache.dram.print(0)

    print("Finish Testing Cache")