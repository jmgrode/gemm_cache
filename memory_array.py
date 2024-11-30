class MemoryArray:
    # Acts like a contiguous array of bytes and allows [] operator to be used
    # Big endian
    def __init__(self, size: int) -> None:
        self.size = size
        self.array = {} # each entry in the dictionary is a byte
        
    def __getitem__(self, key) -> int:
        addr, size = key_to_addr_size(key)
        return self.load(addr, size)

    def __setitem__(self, key, value) -> None:
        addr, size = key_to_addr_size(key)
        self.store(addr, size, value)

    def __delitem__(self, key) -> None:
        addr, size = key_to_addr_size(key)
        self.delete(addr, size)
        
    def load(self, addr: int, size: int) -> int:
        data = 0
        for i in range(size):
            byte = 0
            if (addr + i) in self.array:
                byte = self.array[addr+i]
            assert byte < 256
            data = (data << 8) | byte
        return data
    
    def store(self, addr: int, size: int, data: int) -> None:
        for i in range(size):
            byte = (data >> ((size - i - 1) * 8)) & 0xff
            # byte = (data >> (i * 8)) & 0xff
            self.array[addr + i] = byte
        assert len(self.array) <= self.size
            
    def delete(self, addr: int, size: int) -> None:
        for i in range(size):
            del self.array[addr + i]

    def print(self, starting_addr: int) -> None:
        for addr in sorted(self.array.keys()):
            print(f"Address {starting_addr+addr:08X}: {self.array[addr]:02X}")

def key_to_addr_size(key) -> tuple[int, int]:
    if isinstance(key, slice):
        addr = key.start
        size = key.stop - key.start + 1
    elif isinstance(key, int):
        addr = key
        size = 1
    else:
        assert isinstance(key, slice) or isinstance(key, int)
    return addr, size

if __name__ == "__main__":
    print("MemoryArray Test Begin")
    array = MemoryArray(8)

    # Test store and load functions
    array.store(0, 1, 0xff)
    assert array.load(0, 1) == 0xff
    array.store(1, 3, 0xffffff)
    assert array.load(0,4) == 0xffffffff

    # Test [] operator, __getitem__ and __setitem__, single indexing and slices
    array[35] = 0xf0
    array[32:34] = 0xf0f0f0
    assert array[34:35] == 0xf0f0
    assert array[32] == 0xf0
    array[32] = 1
    assert array[32] == 1

    # Test size assertion
    try:
        array[36] = 0
        print("Failed, should have exceeded max size")
    except AssertionError:
        pass
    
    try:
        array.store(36, 1, 0)
        print("Failed, should have exceeded max size")
    except AssertionError:
        pass
    
    # Test delete
    array.delete(32, 4)
    del array[0:3]
    assert array[0:3] == 0 # All values start out as 0
    assert array[32:35] == 0
    print("MemoryArray Test Finished")
