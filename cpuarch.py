# tiny_cpu.py -- Simple 8-bit CPU emulator (educational)

from typing import List, Tuple

MEM_SIZE = 65536  # 64 KiB memory

class TinyCPU:
    def __init__(self):
        self.mem = [0] * MEM_SIZE
        self.A = 0            # Accumulator (8-bit)
        self.B = 0            # General register (8-bit)
        self.PC = 0           # Program counter (16-bit)
        self.Z = False        # Zero flag
        self.running = True
        self.output = []      # collect OUT values

    def load_program(self, program: List[Tuple[str, int]]):
        """Loads an assembly-like program into memory. Program is list of (mnemonic, operand)"""
        addr = 0
        for instr in program:
            op = instr[0].upper()
            arg = instr[1] if len(instr) > 1 else 0
            # very simple encoding: store textual opcode mapping to bytes for demo
            # We'll encode opcode byte then two bytes operand (if needed)
            opcode = OPCODES_INV[op]
            self.mem[addr] = opcode
            addr += 1
            # store operand as 16-bit little-endian
            self.mem[addr] = arg & 0xFF
            self.mem[addr+1] = (arg >> 8) & 0xFF
            addr += 2
        # mark end with HLT just in case
        self.mem[addr] = OPCODES_INV['HLT']

    def fetch_operand(self):
        lo = self.mem[self.PC]
        hi = self.mem[(self.PC + 1) & 0xFFFF]
        val = lo | (hi << 8)
        self.PC = (self.PC + 2) & 0xFFFF
        return val

    def step(self):
        opcode = self.mem[self.PC]
        self.PC = (self.PC + 1) & 0xFFFF
        # dispatch
        if opcode == OPCODES_INV['LDA']:
            imm = self.fetch_operand() & 0xFF
            self.A = imm
            self.Z = (self.A == 0)
        elif opcode == OPCODES_INV['LDB']:
            imm = self.fetch_operand() & 0xFF
            self.B = imm
            self.Z = (self.B == 0)
        elif opcode == OPCODES_INV['LDA_MEM']:
            addr = self.fetch_operand()
            self.A = self.mem[addr] & 0xFF
            self.Z = (self.A == 0)
        elif opcode == OPCODES_INV['STA']:
            addr = self.fetch_operand()
            self.mem[addr] = self.A & 0xFF
        elif opcode == OPCODES_INV['ADD']:
            # ADD B -> A = A + B (wrap 8-bit)
            s = (self.A + self.B) & 0xFF
            self.A = s
            self.Z = (self.A == 0)
        elif opcode == OPCODES_INV['SUB']:
            s = (self.A - self.B) & 0xFF
            self.A = s
            self.Z = (self.A == 0)
        elif opcode == OPCODES_INV['JMP']:
            addr = self.fetch_operand()
            self.PC = addr & 0xFFFF
        elif opcode == OPCODES_INV['JZ']:
            addr = self.fetch_operand()
            if self.Z:
                self.PC = addr & 0xFFFF
        elif opcode == OPCODES_INV['OUT']:
            # output A
            self.output.append(self.A)
        elif opcode == OPCODES_INV['HLT']:
            self.running = False
        else:
            raise RuntimeError(f"Unknown opcode {opcode} at PC {self.PC-1:04X}")

    def run(self, max_steps=100000):
        steps = 0
        while self.running and steps < max_steps:
            self.step()
            steps += 1
        if steps >= max_steps:
            raise RuntimeError("Max steps reached (possible infinite loop)")

# Simple opcode table
OPCODES = {
    0x01: 'LDA',
    0x02: 'LDB',
    0x03: 'LDA_MEM',
    0x04: 'STA',
    0x05: 'ADD',
    0x06: 'SUB',
    0x07: 'JMP',
    0x08: 'JZ',
    0x09: 'OUT',
    0xFF: 'HLT',
}
# inverse for convenience
OPCODES_INV = {v:k for k,v in OPCODES.items()}

# Example program: compute 7+5 and output (prints 12)
# Program encoding: list of tuples (mnemonic, operand)
# Note: every instruction reserves 2 bytes for operand (unused ones can be 0)
prog = [
    ('LDA', 7),       # A = 7
    ('LDB', 5),       # B = 5
    ('ADD', 0),       # A = A + B
    ('OUT', 0),       # output A
    ('HLT', 0)
]

if __name__ == '__main__':
    cpu = TinyCPU()
    cpu.load_program(prog)
    cpu.run()
    print("Output bytes:", cpu.output)
    print("Output (decimal):", [b for b in cpu.output])
    print("Output (ASCII):", ''.join(chr(b) for b in cpu.output))
