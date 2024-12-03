class Program:
    # this class lets you define the instructions in the program and converts them to a list to be passed into Cpu
    # the implementations of the instructions are in cpu.py
    def __init__(self, register_bytes: int) -> None:
        self.instructions = []
        self.register_bytes = register_bytes
        self.half_register_mask = [0xf, 0xff, 0xfff, 0xffff][register_bytes-1]
        # half of length of each register in number of bytes for use in label_jump translation

	# convert labels to addresses and get instruction list
    def get_instructions(self) -> list[tuple]:
        labels = {}
        label_branch_ifs = []
        label_jumps = []
        for i,instr in enumerate(self.instructions):
            instr_addr = i - len(labels) + 3*len(label_jumps) # account for previous labels which will be removed and adds for jumps
            if instr[0] == "label":
                assert not instr[1] in labels
                labels[instr[1]] = instr_addr
            if instr[0] == "label_branch_if":
                label_branch_ifs.append(instr_addr)
            if instr[0] == "label_jump":
                label_jumps.append(instr_addr)
        for label in labels.keys():
            self.instructions.remove({"label", label})
        for jump_addr in label_jumps:
            assert self.instructions[jump_addr][0] == "label_jump"
            available_register = self.instructions[jump_addr][1]
            label = self.instructions[jump_addr][2]
            dest_addr = labels[label]
            left_half_addr = (dest_addr >> (self.register_bytes/2)) & self.half_register_mask
            right_half_addr = dest_addr & self.half_register_mask
            labeled_jump_to_jump_instrs = [
                ("move", available_register, left_half_addr),
                ("logical_shift_left", available_register, available_register, self.register_bytes*8/2),
                ("move", available_register, right_half_addr)
            ]
            self.instructions[jump_addr:jump_addr] = labeled_jump_to_jump_instrs
        for branch_addr in label_branch_ifs:
            assert self.instructions[branch_addr][0] == "label_branch_if"
            label = self.instructions[branch_addr][2]
            self.instructions[branch_addr][2] = labels[self.instructions[branch_addr][2]]
		#TODO: test this function (test whether labels work)
        return self.instructions

    def halt(self) -> None:
        self.instructions.append(("halt",)) # comma required to make single element tuple

    def insert_label(self, label: str) -> None:
        self.instructions.append(("label", label))

    def label_branch_if(self, cond_register: int, label: str) -> int: # label is converted into offset from label
        self.instructions.append(("label_branch_if", cond_register, label))

    def label_jump(self, available_register, label: str) -> int: # label address is moved into available_register to jump
        self.instructions.append(("label_jump", available_register, label))

    def load(self, dest_register: int, addr_register: int, immediate: int) -> None:
        self.instructions.append(("load", dest_register, addr_register, immediate))
        
    def store(self, src_register: int, addr_register: int, immediate: int) -> None:
        self.instructions.append(("store", src_register, addr_register, immediate))

    def move_memory(self, src_addr_register: int, dest_addr_register: int, size_register: int) -> None:
        self.instructions.append(("move_memory", src_addr_register, dest_addr_register, size_register))

    def move(self, dest_register: int, immediate: int) -> int:
        self.instructions.append(("move", dest_register, immediate))

    def add_immediate(self, dest_register: int, src_register: int, immediate: int) -> int:
        self.instructions.append(("add_immediate", dest_register, src_register, immediate))

    def add(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.instructions.append(("add", dest_register, src_register1, src_register2))

    def multiply(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.instructions.append(("multiply", dest_register, src_register1, src_register2))

    def branch_if(self, cond_register: int, immediate: int) -> int:
        self.instructions.append(("branch_if", cond_register, immediate))

    def jump(self, dest_register: int) -> int:
        self.instructions.append(("jump", dest_register))

    def bitwise_or(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.instructions.append(("bitwise_or", dest_register, src_register1, src_register2))

    def bitwise_and(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.instructions.append(("bitwise_and", dest_register, src_register1, src_register2))

    def bitwise_xor(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.instructions.append(("bitwise_xor", dest_register, src_register1, src_register2))

    def bitwise_nor(self, dest_register: int, src_register1: int, src_register2: int) -> int:
        self.instructions.append(("bitwise_nor", dest_register, src_register1, src_register2))
    
    def bitwise_not(self, dest_register: int, src_register: int) -> int:
        self.instructions.append(("bitwise_not", dest_register, src_register))
    
    def logical_shift_left(self, dest_register: int, value_register: int, shift_size_register: int) -> int:
        self.instructions.append(("logical_shift_left", dest_register, value_register, shift_size_register))

    def logical_shift_right(self, dest_register: int, value_register: int, shift_size_register: int) -> int:
        self.instructions.append(("logical_shift_right", dest_register, value_register, shift_size_register))

    def matrix_multiply(self, dest_addr_register: int, src_addr_register1: int, src_addr_register2: int) -> int:
        self.instructions.append(("matrix_multiply", dest_addr_register, src_addr_register1, src_addr_register2))

    def matrix_add(self, dest_addr_register: int, src_addr_register1: int, src_addr_register2: int) -> int:
        self.instructions.append(("matrix_add", dest_addr_register, src_addr_register1, src_addr_register2))
