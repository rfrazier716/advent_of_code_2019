import numpy as np
import copy


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
    def __init__(self, memory=np.array([]), verbose=False):

        self._verbose = verbose  # Used for Debug, print computer flow to console

        self._parameter_array = np.full(3, 0, dtype=int)  # Array that holds parameters mode settings for arguments
        self._registers = np.full(3, 0,dtype=np.int64)  # the three registers used for all operations

        self.__shadow_memory = copy.deepcopy(memory)  # the default state of memory used for reboots
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
        self._extended_memory = {}  # Extended memory is a dictionary
        self._relative_offset = 0  # relative offset for referencing memory locations
        self._memory = copy.deepcopy(self.__shadow_memory).astype(np.int64)  # restore the memory to a default state
        self._input_buffer = []  # reset the input buffer
        self._output_buffer = []
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

    def load_memory(self, memory):
        # load a new array of memory into computer and reset
        self.__shadow_memory = copy.deepcopy(memory)
        self.reset()

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

    def _write_to_memory(self, memory_address, value):
        try:
            self._memory[memory_address] = value
        except IndexError:
            # If there's an index error write the value to extended memory
            self._extended_memory[memory_address] = value

    def _load_registers(self, opcode):
        # load registers based on the number of parameters the opcode needs and the parameter type
            # if the opmode doesn't write to memory pull it as normal, if it does write to memory you have to treat
            # that last instruction special so the address to write to get passed instead of the value in that address
        for j in range(opcode.n_params):
            #have to have special cases to make sure the register address is passed instead of register value for operations that write to memory
            if opcode.writes_to_memory and j==opcode.n_params-1:
                if self._parameter_array[j]==0 or self._parameter_array[j]==1: self._registers[j]=self._parameter_mode[1]()  #pass the value from memory which is what register to write to
                elif self._parameter_array[j]==2: self._registers[j]=self._parameter_mode[1]()+self._relative_offset #pass the value from memory plus offset
            else:
                # check which parameter mode is needed and call the appropriate function
                self._registers[j]=self._parameter_mode[self._parameter_array[j]]()



    def cycle(self):
        if self._running and not self._program_finished:
            if self._verbose:
                print("Pulling Instruction from memory address {}".format(self._pc))
            opcode = self._pull_instruction()  # pull an instruction and advance the program counter
            if opcode.writes_to_memory and self._parameter_array[opcode.n_params - 1] == 0 :
                # If this isn't an output the final bit of the param register has to be 1 because that specifies which register is written to
                # output can just output an immediate value
                self._parameter_array[opcode.n_params - 1] = 1

            # fill the data registers by pulling from memory the required number of parameters
            self._load_registers(opcode)
            if self._verbose:
                print("\t Opcode: {}:{}".format(opcode.value, opcode.descriptor) + ",Parameter modes: {}{}{}".format(
                    *self._parameter_array))
                i = 0
                for reg in self._registers:
                    print("\t Register {}:\t{}".format(i, reg))
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
        return self._pull_from_memory(self._pc_pull())

    def _param_immediate(self):
        return self._pc_pull()

    def _param_relative(self):
        return self._pull_from_memory(self._pc_pull() + self._relative_offset)

    # Opcode functions defined below

    def _op_add(self):
        # add the values in register 0 and 1 and store in memory location pointed to by reg 2
        self._write_to_memory(self._registers[2], self._registers[0] + self._registers[1])

    def _op_multiply(self):
        # multiply the values in register 0 and 1 and store in memory location pointed to by reg 2
        self._write_to_memory(self._registers[2], self._registers[0] * self._registers[1])

    def _op_input(self):
        # pop a value from the input buffer in fifo format and write to the memory address in register[0]
        try:
            self._write_to_memory(self._registers[0], self._input_buffer.pop(0))
        except IndexError:  # Index error occurs because we tried to pop from an empty list, need to suspend execution until we have input
            self._pc -= 2  # decrement the program counter twice so that when the system resumes it's at the input instruction
            self._running = False

    def _op_output(self):
        # take value in register[0] and puts it on the output buffer
        self._output_buffer.append(self._registers[0])

    def _op_jmp_if_true(self):
        # if the value of the reg 0 is not zero, set the program counter to the value of register 1
        if self._registers[0] != 0:
            self._pc = self._registers[1]

    def _op_jmp_if_false(self):
        # if the value of the reg 0 is zero, set the program counter to the value of register 1
        if self._registers[0] == 0:
            self._pc = self._registers[1]

    def _op_less_than(self):
        result = 0
        if self._registers[0] < self._registers[1]:
            result = 1
        self._write_to_memory(self._registers[2], result)
        pass

    def _op_equal_to(self):
        result = 0
        if self._registers[0] == self._registers[1]:
            result = 1
        self._write_to_memory(self._registers[2], result)
        pass

    def _op_set_relative_offest(self):
        self._relative_offset += self._registers[0]

    def _op_terminate(self):
        self._program_finished = True
