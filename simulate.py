from cpu import Cpu
from dram import Dram
from gemm_cache import GemmCache, Cache

# TODO: determine how to time everything

class Simulator:
    def __init__(self, cpu: Cpu) -> None:
        self.cpu = Cpu
        self.time = 0

    def reset(self):
        pass
		# reset after a simulation

    def simulate(self, instructions):
        pass
        #TODO: figure out what type instructions should be, probably a list of tuples which contain the arguments for instruction functions