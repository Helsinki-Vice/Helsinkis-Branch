from typing import TYPE_CHECKING
from urclToISA.operand import OpType
from urclToISA.UTRX import Translation
from urclToISA.program import Program
if TYPE_CHECKING: from urclToISA.instruction import Instruction

class Translator():
    def __init__(self, translations: dict[str, Translation]):
        self.translations = translations

    def substitute(self, ins: "Instruction"):
        translation = self.translations.get(ins.opcode)
        if translation is None:
            return []
        body = ins.match(translation)
        if body is None:
            return []
        for l,line in enumerate(body):
            for i in range(len(ins.operands)):
                body[l] = body[l].replace(f"@{chr(65+i)}", str(ins.operands[i]))
        return body

    def substitute_urcl(self, ins: "Instruction"):
        translation = self.translations.get(ins.opcode)
        if translation is None:
            return None
        body = ins.match(translation)
        if body is None:
            return None
        sub = Program.parse(body)
        for i,instr in enumerate(sub.code):
            for o,opr in enumerate(instr.operands):
                if opr.type == OpType.OTHER:
                    if opr.value.isalpha() and len(opr.value) == 1:
                        placeholder = ins.operands[ord(opr.value)-65]
                        opr.extra[opr.value] = placeholder
        return sub

    @staticmethod
    def from_file(filename):
        translations = Translation.parse_file(filename)
        return Translator(translations)