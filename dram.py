from packet import Packet
from memory import MemObject
from memory_array import MemoryArray
import sys

class Dram(MemObject):
    def __init__(self, size: int, read_latency: int, write_latency: int, burst_size: int = 64) -> None:
        super().__init__(size, size, read_latency, write_latency)
        self.memory = MemoryArray(size)
        self.read_latency = read_latency
        self.write_latency = write_latency
        self.burst_size = burst_size

    def process_packet(self, pkt: Packet) -> Packet:
        if (pkt.addr < 0) or (pkt.addr + pkt.size > len(self.memory)):
            sys.exit("Error: out of bounds load or store to DRAM")

        if (pkt.load):
            return self.retrieve(pkt)
        return self.store(pkt)

    def retrieve(self, pkt: Packet) -> Packet:
        data = self.memory[pkt.addr : pkt.addr + pkt.size]
        latency = (pkt.size // self.burst_size) * self.read_latency + pkt.latency
        return Packet(True, pkt.addr, pkt.size, data, latency)

    def store(self, pkt: Packet) -> Packet:
        self.memory[pkt.addr : pkt.addr + pkt.size] = pkt.data
        latency = (pkt.size // self.burst_size) * self.write_latency + pkt.latency
        return Packet(False, pkt.addr, 0, None, latency)

if __name__ == "__main__":
    print("Testing DRAM")

    DRAM_obj = Dram(size = 2048, read = 10, write = 12)

    # test write
    num_bytes = 256
    data = (1 << num_bytes * 8) - 1 # 8 bits per byte
    pkt_write = Packet(load=False, addr=7, size=num_bytes, data=data, latency=0)
    pkt_write_ret = DRAM_obj.process_packet(pkt_write)
    assert(pkt_write_ret.load == False)
    assert(pkt_write_ret.addr == 7)
    assert(pkt_write_ret.size == 0)
    assert(pkt_write_ret.data == None)
    assert(pkt_write_ret.latency = (256 / 64) * 12)

    # test read
    pkt_read = Packet(load=True, addr=7, size=num_bytes, data=None, latency = pkt_write_ret.latency)
    pkt_read_ret = DRAM_obj.process_packet(pkt_read)
    assert(pkt_read_ret.load == True)
    assert(pkt_read_ret.addr == 7)
    assert(pkt_read_ret.size == num_bytes)
    assert(pkt_read_ret.data == data)
    assert(pkt_read_ret.latency = (256 / 64) * 12 + (256 / 64) * 10)   

    # test another read
    expected_data = data & (data - 1)
    pkt_read = Packet(load=True, addr=8, size=num_bytes, data=None, latency = pkt_read_ret.latency)
    pkt_read_ret = DRAM_obj.process_packet(pkt_read)
    assert(pkt_read_ret.data == expected_data)

    # test out of bounds
    pkt_oob = Packet(load=True, addr=2040, size=num_bytes, data=data, latency = pkt_read_ret.latency)
    try:
        dram_obg.process_packet(pkt_oob)
    except SystemExit as e:
        pass
    else:
        assert(False)



    