import unittest
from urclToISA.instruction import Instruction
from urclToISA.operand import Operand, OpType

class MyTest(unittest.TestCase):

    def test_working(self):
        instruction = Instruction.parse("add r1 r2 r3")
        if instruction:
            self.assertEqual(instruction.opcode, "ADD")
        self.assertIsNotNone(instruction)
    
    def test_instruction_should_parse(self):
        #TODO: stack pointer support
        should_parse: list[tuple["Instruction | None", str, list[OpType]]] = [
            (Instruction.parse("ADD r1 r2 r3"), "ADD", [OpType.REGISTER, OpType.REGISTER, OpType.REGISTER]),
            (Instruction.parse("Add\t$1 6 6"), "ADD", [OpType.REGISTER, OpType.NUMBER, OpType.NUMBER]),
            #(Instruction.parse(" ADD R1 -2 SP "), "ADD", [OpType.REGISTER, OpType.NEGATIVE, OpType.STACKPTR]),
            (Instruction.parse("HLT \t \t"), "HLT", []),
            (Instruction.parse("jmp m6"), "JMP", [OpType.ADDRESS]),
            (Instruction.parse("bnz .label r0 r3"), "BNZ", [OpType.LABEL, OpType.REGISTER, OpType.REGISTER]),
            (Instruction.parse("  lod $01 .label"), "LOD", [OpType.REGISTER, OpType.LABEL]),
            #(Instruction.parse("  lod sp ~-42"), "LOD", [OpType.STACKPTR, OpType.RELATIVE]),
            (Instruction.parse("out %numb  -006969"), "OUT", [OpType.PORT, OpType.NEGATIVE])
        ]
        for tup in should_parse:
            instruction, opcode, argument_types = tup
            if instruction:
                self.assertEqual(instruction.opcode, opcode)
                for n in range(len(instruction.operands)):
                    self.assertEqual(instruction.operands[n].type, argument_types[n])
            self.assertIsNotNone(instruction)