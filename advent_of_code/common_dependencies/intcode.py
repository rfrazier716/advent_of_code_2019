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
        self._registers = np.full(3, 0)  # the three registers used for all operations

        self.__shadow_memory = copy.deepcopy(memory)  # the default state of memory used for reboots
        self.reset()    #reset the computer

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
            Opcode(99, 0, self._op_terminate, False, "Terminate")

        )}

    def reset(self):
        # Reset the computer by setting the pc to 0x00 and setting _running to True
        self._memory = copy.deepcopy(self.__shadow_memory) # restore the memory to a default state
        self._input_buffer = []  # reset the input buffer
        self._output_buffer=[]
        self._pc = 0x00  # Program counter for traversing memory

        self._running = True    # Boolean that states whether the code is running or blocked waiting for input
        self._program_finished = False # Flag that gets set when opcode 99 is read

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

    def _reset_parameter_array(self):
        self._parameter_array = np.full(3, 0, dtype=int)

    def _pull_instruction(self):
        # takes in a parameterized opcode from memory, returns the opcode and updates the parameter array
        instruction = self._memory[self._pc]  # pull the instruction from memory based on the program counter
        self._pc += 1  # increment the program counter
        number_arr = np.array([int(d) for d in str(instruction).zfill(5)], dtype=int)
        opcode_val = number_arr[-1] + 10 * number_arr[-2]  # the last two values are opcode

        # populate parameter array
        self._parameter_array = np.flip(
            number_arr[0:3])  # load in reverse order because the furthest byte is parameter 3
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
        self._running=True
        self.run()

    def _load_registers(self, n_params):
        # load registers based on the number of parameters the opcode needs and the parameter type
        for j in range(n_params):
            if self._parameter_array[j] == 0:
                # if the parameter array is 0 it is a position mode command and the value at the memory location is pulled into the register
                self._registers[j] = self._memory[self._pc_pull()]
            elif self._parameter_array[j] == 1:
                # if the parameter array is 1 it is an immediate mode parameter and the contents pulled from memory gets pulled into the register
                self._registers[j] = self._pc_pull()
            else:
                raise ValueError("Expected a 0 or 1 but got {}".format(self._parameter_array[j]))

    def cycle(self):
        if self._running and not self._program_finished:
            if self._verbose:
                print("Pulling Instruction from memory address {}".format(self._pc))
            opcode = self._pull_instruction()  # pull an instruction and advance the program counter
            if opcode.writes_to_memory:
                # If this isn't an output the final bit of the param register has to be 1 because that specifies which register is written to
                # output can just output an immediate value
                self._parameter_array[opcode.n_params - 1] = 1

            self._load_registers(
                opcode.n_params)  # fill the data registers by pulling from memory the required number of parameters
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
    def valid_opcodes(self):
        return [opcode.value for opcode in self._opcodes]

    @property
    def memory(self):
        return self._memory

    @property
    def output_waiting(self):
        # Outputs how many outputs are waiting on the output buffer
        return len(self._output_buffer)

    # Opcode functions defined below

    def _op_add(self):
        # add the values in register 0 and 1 and store in memory location pointed to by reg 2
        self._memory[self._registers[2]] = self._registers[0] + self._registers[1]

    def _op_multiply(self):
        # multiply the values in register 0 and 1 and store in memory location pointed to by reg 2
        self._memory[self._registers[2]] = self._registers[0] * self._registers[1]

    def _op_input(self):
        # pop a value from the input buffer in fifo format and write to the memory address in register[0]
        try:
            self._memory[self._registers[0]] = self._input_buffer.pop(0)
        except IndexError:  #Index error occurs because we tried to pop from an empty list, need to suspend execution until we have input
            self._pc-=2 #decrement the program counter twice so that when the system resumes it's at the input instruction
            self._running=False

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
        self._memory[self._registers[2]] = result
        pass

    def _op_equal_to(self):
        result = 0
        if self._registers[0] == self._registers[1]:
            result = 1
        self._memory[self._registers[2]] = result
        pass

    def _op_terminate(self):
        self._program_finished = True

