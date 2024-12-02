from packet import Packet
from memory import MemObject
from memory_array import MemoryArray
import math

class Dram(MemObject):
    def __init__(self, size: int, read_latency: int, write_latency: int, burst_size: int = 64) -> None:
        super().__init__(size, size, read_latency, write_latency)
        assert burst_size > 0, "Burst size must be greater than 0"

        self.memory = MemoryArray(size)
        self.mem_size = size
        self.read_latency = read_latency
        self.write_latency = write_latency
        self.burst_size = burst_size

    def process_packet(self, pkt: Packet) -> Packet:
        assert pkt.size > 0, "Error: Packet size must be greater than 0 for DRAM load/store"
        assert (pkt.addr >= 0) and (pkt.addr + pkt.size <= self.mem_size), "Error: out of bounds load or store to DRAM"

        if (pkt.load):
            return self.retrieve(pkt)
        return self.store(pkt)

    def set_value(self, addr: int, size: int, value: int) -> None:
        # assert math.ceil(value.bit_length() / 8) == size, "Error: Data size mismatch with variable size during DRAM load/store"
        self.memory.store(addr, size, value)

    def retrieve(self, pkt: Packet) -> Packet:
        pkt.data = self.memory[pkt.addr : pkt.addr + pkt.size]
        pkt.latency += (pkt.size // self.burst_size) * self.read_latency
        return pkt

    def store(self, pkt: Packet) -> Packet:
        # assert math.ceil(pkt.data.bit_length() / 8) == pkt.size, "Error: Data size mismatch with variable size during DRAM load/store"
        self.memory[pkt.addr : pkt.addr + pkt.size] = pkt.data
        pkt.latency += (pkt.size // self.burst_size) * self.write_latency
        return pkt
    
    def print(self, starting_addr: int) -> None:
        self.memory.print(starting_addr)

if __name__ == "__main__":
    print("Testing DRAM")

    DRAM_obj = Dram(size=2048, read_latency=10, write_latency=12)

    # test write
    num_bytes = 256
    data = (1 << num_bytes * 8) - 1 # 8 bits per byte
    pkt_write = Packet(load=False, addr=7, size=num_bytes, data=data, latency=0)
    pkt_write_ret = DRAM_obj.process_packet(pkt_write)
    assert(pkt_write_ret.load == False)
    assert(pkt_write_ret.addr == 7)
    assert(pkt_write_ret.size == num_bytes)
    assert(pkt_write_ret.data == data)
    assert(pkt_write_ret.latency == (256 / 64) * 12)

    # test read
    pkt_read = Packet(load=True, addr=7, size=num_bytes, data=None, latency = pkt_write_ret.latency)
    pkt_read_ret = DRAM_obj.process_packet(pkt_read)
    assert(pkt_read_ret.load == True)
    assert(pkt_read_ret.addr == 7)
    assert(pkt_read_ret.size == num_bytes)
    assert(pkt_read_ret.data == data)
    assert(pkt_read_ret.latency == (256 / 64) * 12 + (256 / 64) * 10)   

    # test out of bounds
    pkt_oob = Packet(load=True, addr=2040, size=num_bytes, data=data, latency = pkt_read_ret.latency)
    try:
        DRAM_obj.process_packet(pkt_oob)
    except AssertionError as e:
        pass
    else:
        assert(False)

    # test another read
    expected_data = data << 8
    pkt_read = Packet(load=True, addr=8, size=num_bytes, data=None, latency = pkt_read_ret.latency)
    pkt_read_ret = DRAM_obj.process_packet(pkt_read)
    assert(pkt_read_ret.data == expected_data)

    print("Finished Testing DRAM")



    