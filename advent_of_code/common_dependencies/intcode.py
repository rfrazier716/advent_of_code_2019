import numpy as np
import copy

def multiply(a,b):
    #multiply function for intcode computer
    return a*b

def add(a,b):
    #add function for intcode computer
    return a+b

class IntcodeComputer():
    def __init__(self,memory=np.array([])):
        self._pc=0x00 #Program counter for traversing memory
        self._reg_a=0x00 #register A, used for operations
        self._reg_b=0x00 #register B, used for operations
        self._reg_c=0x00 #register C, holds the memory address of the result of an operation
        self._opcode=0x00 #Opcode is the command given to the computer

        self._running=True  # Current state of the computer,
        self._memory=copy.deepcopy(memory) #the "memory of the computer" a 1D array of integer values

    @property
    def memory(self):
        return self._memory

    def reset(self):
        #Reset the computer by setting the pc to 0x00 and setting _running to True
        self._pc=0x00
        self._running=True

    def load_memory(self,memory):
        #load a new array of memory into computer and reset
        self._memory=copy.deepcopy(memory)
        self.reset()

    def _load_opcode(self):
        self._opcode=self._memory[self._pc]
        if self._opcode not in [1,2,99]:
            #if you don't have a valid opcode raise an error
            raise ValueError("Loaded an Invalid Opcode from memory address {:04x}, got: {:04x}".format(self._pc,self._opcode))
        elif self._opcode==99:
            # computer received opcode to terminate program
            self._running=False
        else:
            self._pc+=1

    def _pc_pull(self):
        #pull from the memory address pointed to by the program counter and increment by one
        data=self._memory[self._pc]
        self._pc+=1
        return data

    def run(self):
        # Runs the computer until it it shutdown by an opcode and then returns the memory space
        while self._running:
            self.cycle()
        return self._memory

    def _execute_instruction(self):
        opcode_dict={
            1: add,
            2: multiply
        }
        self._memory[self._reg_c]=opcode_dict.get(self._opcode)(self._reg_a,self._reg_b)

    def cycle(self):
        if self._running:
            self._load_opcode() # pull an opcode and advance the program counter
            if self._running: #have to check if it's still running after pulling the opcode
                self._reg_a=self._memory[self._pc_pull()]# pull the value into register A, advance PC
                self._reg_b=self._memory[self._pc_pull()] # pull the value into register B, advance PC
                self._reg_c=self._pc_pull() # pull the memory location of the result into register C
                self._execute_instruction()
        else:
            raise ValueError("Tried to cycle computer but it is not running")

        # execute the opcode

