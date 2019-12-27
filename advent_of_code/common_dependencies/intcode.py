import numpy as np
import copy
from collections import defaultdict


class Opcode():
    def __init__(self, value, n_params, function, writes_to_memory, descriptor=""):
        self.value = value  # the integer value of the opcode
        self.n_params = n_params  # number of parameters the opcode requires
        self.writes_to_memory = writes_to_memory  # tracks if this opcode writes the result of the operation to memory
        self.function = function  # function to execute when the opcode is called
        self.descriptor = descriptor  # human readable descriptor

    def execute(self):
        self.function()


class IntcodeComputer():
    def __init__(self, software=[], verbose=False):

        self._verbose = verbose  # Used for Debug, print computer flow to console

        self._parameter_array = np.full(3, 0, dtype=int)  # Array that holds parameters mode settings for arguments
        self._registers = np.full(3, 0,dtype=np.int64)  # the three registers used for all operations, these registers hold memory locations that the operators act on

        self._software=software  # this is the software that has to be loaded into memory
        self.reset()  # reset the computer

        # This is the list of current opcodes for the computer
        self._opcodes = {code.value: code for code in (
            Opcode(1, 3, self._op_add, True, "Add"),
            Opcode(2, 3, self._op_multiply, True, "Multiply"),
            Opcode(3, 1, self._op_input, True, "Input"),
            Opcode(4, 1, self._op_output, False, "Output"),
            Opcode(5, 2, self._op_jmp_if_true, False, "Jump if True"),
            Opcode(6, 2, self._op_jmp_if_false, False, "Jump if False"),
            Opcode(7, 3, self._op_less_than, True, "Less Than operator"),
            Opcode(8, 3, self._op_equal_to, True, "Equal To Operator"),
            Opcode(9, 1, self._op_set_relative_offest, False, "Set Relative offset"),
            Opcode(99, 0, self._op_terminate, False, "Terminate")

        )}

        # parameter mode dictionary for handling what values are passed to registers
        self._parameter_mode = {
            0: self._param_position,
            1: self._param_immediate,
            2: self._param_relative
        }

    def reset(self):
        # Reset the computer by setting the pc to 0x00 and setting _running to True
        self._memory=defaultdict(np.int64)   #memory is a dictionary with default value of 0 for nonexistant keys
        self._relative_offset = 0  # relative offset for referencing memory locations
        for index,value in enumerate(self._software):
            # restore the memory to a default state
            self._memory[index]=np.int64(value)
        self._input_buffer = []  # reset the input buffer
        self._output_buffer = [] # reset the output buffer
        self._pc = 0x00  # Program counter for traversing memory

        self._running = True  # Boolean that states whether the code is running or blocked waiting for input
        self._program_finished = False  # Flag that gets set when opcode 99 is read

    def input(self, input):
        # pushes an input to the end of the input buffer
        self._input_buffer.append(input)

    def get_output(self):
        # pops one value from the output buffer and returns it
        return self._output_buffer.pop(0)

    def flush_output(self):
        # pops items from the output buffer and prints them
        tmp = self._output_buffer  # assign the buffer to a temporary variable
        self._output_buffer = []  # clear the buffer
        return tmp  # return the buffer

    def load_software(self, software):
        # load a new array of memory into computer and reset
        self._software=software
        self.reset()

    def load_memory(self,software):
        print("This function has been replaced by \"load_software()\"")
        self.load_software(software)

    def _pull_instruction(self):
        # takes in a parameterized opcode from memory, returns the opcode and updates the parameter array
        instruction = self._memory[self._pc]  # pull the instruction from memory based on the program counter
        self._pc += 1  # increment the program counter
        number_arr = np.array([int(d) for d in str(instruction).zfill(5)], dtype=int)

        opcode_val = number_arr[-1] + 10 * number_arr[-2]  # the last two values are opcode

        # populate parameter array
        # load in reverse order because the furthest byte is parameter 3
        self._parameter_array = np.flip(number_arr[0:3])
        if self._verbose: print(number_arr)
        try:
            return self._opcodes[opcode_val]  # return the opcode from dictionary lookup
        except KeyError:
            raise ValueError(
                "Loaded an Invalid Opcode from memory address {}, got: {}".format(self._pc, opcode_val))

    def _pc_pull(self):
        # pull from value memory address pointed to by the program counter and increment by one
        data = self._memory[self._pc]
        self._pc += 1

        return data

    def run(self):
        # Runs the computer until it it shutdown by an opcode and then returns the memory space
        while self._running and not self._program_finished:
            self.cycle()
        return self._memory

    def resume(self):
        # resumes operation of the computer but does not reset the state, used if it hangs while waiting for user input
        self._running = True
        self.run()

    def _pull_from_memory(self, memory_address):
        try:
            # Try to access the value from normal program memory
            return self._memory[memory_address]
        except IndexError:
            # If there's an index error pull the value from extended memory
            return self._extended_memory.get(memory_address, 0)

    def _load_registers(self, opcode):
        #load registers with the addresses where they can find the values required for operations
        self._registers=[self._parameter_mode[parameter]() for parameter in self._parameter_array[0:opcode.n_params]]

    def cycle(self):
        if self._running and not self._program_finished:
            if self._verbose:
                print("relative offset {}".format(self._relative_offset))
                print("Pulling Instruction from memory address {}".format(self._pc))
            opcode = self._pull_instruction()  # pull an instruction and advance the program counter

            # fill the data registers by pulling from memory the required number of parameters
            self._load_registers(opcode)
            if self._verbose:
                print("\t Opcode: {}:{}".format(opcode.value, opcode.descriptor) + ", Parameter modes: {}{}{}".format(
                    *self._parameter_array))
                i = 0
                for reg in self._registers:
                    print("\t Register {}:\t{} ({})".format(i, reg,self._memory[reg]))
                    i += 1
            opcode.execute()  # execute the opcode
            # if self._verbose: print(self._memory)
        else:
            raise ValueError("Tried to cycle computer but it is not running")

    # Object Properties
    @property
    def program_finished(self):
        return self._program_finished

    @property
    def valid_opcodes(self):
        return [opcode.value for opcode in self._opcodes]

    @property
    def memory(self):
        return self._memory

    @property
    def output_waiting(self):
        # Outputs how many outputs are waiting on the output buffer
        return len(self._output_buffer)

    # parameter mode functions defined below
    def _param_position(self):
        #the memory address pointed to by the PC holds a reference to which address holds teh data to operate on
        return self._pc_pull()

    def _param_immediate(self):
        #the memory address pointed to by the PC holds the data to operate on
        index = self._pc #store the memory address the pc is pointing to
        self._pc +=1    #increment the program counter
        return index

    def _param_relative(self):
        #the memory address pointed to by the pc holds a reference to which address holds the data (shifted by offset)
        return self._pc_pull() + self._relative_offset

    # Opcode functions defined below

    def _op_add(self):
        # add the values in register 0 and 1 and store in memory location pointed to by reg 2
        self._memory[self._registers[2]]= self._memory[self._registers[0]] + self._memory[self._registers[1]]

    def _op_multiply(self):
        # multiply the values in register 0 and 1 and store in memory location pointed to by reg 2
        self._memory[self._registers[2]] = self._memory[self._registers[0]] * self._memory[self._registers[1]]

    def _op_input(self):
        # pop a value from the input buffer in fifo format and write to the memory address in register[0]
        try:
            self._memory[self._registers[0]]= self._input_buffer.pop(0)
        except IndexError:  # Index error occurs because we tried to pop from an empty list, need to suspend execution until we have input
            self._pc -= 2  # decrement the program counter twice so that when the system resumes it's at the input instruction
            self._running = False

    def _op_output(self):
        # take value in register[0] and puts it on the output buffer
        self._output_buffer.append(self._memory[self._registers[0]])

    def _op_jmp_if_true(self):
        # if the value of the reg 0 is not zero, set the program counter to the value of register 1
        if self._memory[self._registers[0]] != 0:
            self._pc = self._memory[self._registers[1]]

    def _op_jmp_if_false(self):
        # if the value of the reg 0 is zero, set the program counter to the value of register 1
        if self._memory[self._registers[0]] == 0:
            self._pc = self._memory[self._registers[1]]

    def _op_less_than(self):
        result = 0
        if self._memory[self._registers[0]] < self._memory[self._registers[1]]:
            result = 1
        self._memory[self._registers[2]]= result
        pass

    def _op_equal_to(self):
        result = 0
        if self._memory[self._registers[0]] == self._memory[self._registers[1]]:
            result = 1
        self._memory[self._registers[2]]= result
        pass

    def _op_set_relative_offest(self):
        self._relative_offset += self._memory[self._registers[0]]

    def _op_terminate(self):
        self._program_finished = True
