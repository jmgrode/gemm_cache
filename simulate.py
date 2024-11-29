from cpu import Cpu
from dram import Dram
from gemm_cache import GemmCache, Cache

class Simulator:
    def __init__(self, cpu: Cpu) -> None:
        self.cpu = cpu
        self.time = 0

    def reset(self):
		# reset after a simulation
        self.cpu.pc = 0
        #TODO: reset memories

    def simulate(self, instructions: list):
        # instructions is a list of tuples with instruction name string followed by operands, e.g. ("add", 1, 2)
        #TODO: figure out how to handle pc and branches
        print("Beginning Simulation")
        for instr in instructions:
            instr_func = self.cpu.get_instruction(instr[0])
            self.time += instr_func(*instr[1:])
        print("Simulation Finished!")
        self.cpu.print_registers()
        #TODO: if/where to include fetch latency; probably just add as a fixed value to all cpu instructions

#TODO: finish simulator
#TODO: write assembly programs
#TODO: test everything