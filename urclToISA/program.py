from urclToISA.operand import Operand, OpType
from urclToISA.instruction import Instruction
from enum import Enum
from colorama import init

init(autoreset=True)

HEADER_TYPES = [
    "BITS",
    "MINREG",
    "MINHEAP",
    "RUN",
    "MINSTACK"
]

class HeaderType(Enum):
    BITS = "BITS"
    MINREG = "MINREG"
    MINHEAP = "MINHEAP"
    RUN = "RUN"
    MINSTACK = "MINSTACK"

Header = Enum("Header", " ".join(HEADER_TYPES)) #old

class Program():
    def __init__(self, code:list[Instruction]=[], headers:dict[HeaderType, str]={}, regs:list[str]=[]):
        self.code = code
        self.headers = headers
        self.regs: list[str] = regs
        "Register names"
        self.uid: int = 0
        "Program.unique_labels uses this to count unique labels"

    def make_regs_numeric(self):
        "Renames the registers to be numeric strings ('1', '2', '3', ...)"
        for i,ins in enumerate(self.code):
            for o,opr in enumerate(ins.operands):
                if opr.type == OpType.REGISTER and opr.value != "0":
                    self.code[i].operands[o].value = str(1+self.regs.index(opr.value))
        for r,reg in enumerate(self.regs):
            self.regs[r] = str(r+1)

    def prime_regs(self):
        "Adds \" ' \" to the end of all register names"
        for r,reg in enumerate(self.regs):
            if reg != "0":
                self.rename(reg, reg+"'")
            self.regs[r] = reg+"'"


    def unique_labels(self, uid=0) -> int:
        "Appends a number to label names to make them unique, returns number of labels + starting uid"
        labels = {}
        # First pass update definitions
        for i,ins in enumerate(self.code):
            for l,label in enumerate(ins.labels):
                labels[label.value] = f"{label.value}_{uid}"
                self.code[i].labels[l].value = labels[label.value]
                uid += 1
        # Second pass update references
        for i,ins in enumerate(self.code):
            for o,opr in enumerate(ins.operands):
                if opr.type == OpType.LABEL:
                    self.code[i].operands[o].value = labels[opr.value]
        return uid

    def insert_sub(self, program: "Program", index=-1):
        self.uid = program.unique_labels(self.uid)
        self.replace(program, index)

    def replace(self, program: "Program", index=-1):
        self.code[index:index+1] = program.code
        self.regs = list(set(self.regs + program.regs))

    def insert(self, program: "Program", index=-1):
        self.code[index:index] = program.code
        self.regs = list(set(self.regs + program.regs))

    def rename(self, oldname: str, newname: str, type=OpType.REGISTER):
        "Renames registers, does nothing if use change type=Optype.REGISTER"
        operand_to_rename = None
        for i,ins in enumerate(self.code):
            for o,opr in enumerate(ins.operands):
                if opr.type == type and opr.value == oldname:
                    self.code[i].operands[o].value = newname
                    operand_to_rename = opr
        if operand_to_rename:
            if operand_to_rename.type == OpType.REGISTER:
                self.regs[self.regs.index(oldname)] = newname

    def unpack_placeholders(self):
        for i,ins in enumerate(self.code):
            for o,opr in enumerate(ins.operands):
                if opr.type == OpType.OTHER:
                    if opr.value.isalpha() and len(opr.value) == 1:
                        self.code[i].operands[o] = opr.extra[opr.value]

    def relatives_to_labels(self):
        for i,ins in enumerate(self.code):
            for o,opr in enumerate(ins.operands):
                if opr.type == OpType.RELATIVE:
                    self.code[i + int(opr.value)].labels.append(Operand.parse(f".{ins.opcode}_{self.uid}"))
                    self.code[i].operands[o] = Operand.parse(f".{ins.opcode}_{self.uid}")
                    self.uid += 1

    @staticmethod
    def parse(program: list[str]):
        headers: dict[HeaderType, str] = {}
        code: list[Instruction] = []
        regs: list[str] = []
        program = preprocess_source(str.join("\n", program)).splitlines()
        for line in program:
            header = Program.parse_header(line)
            if header is not None:
                headers.update(header)
                continue
            ins = Instruction.parse(line)
            if ins is None:
                continue
            if len(code) > 0:
                if code[-1].opcode == "NOP":
                    if code[-1].labels is not None:
                        ins.labels += code[-1].labels
                    code = code[:-1]
            for operand in ins.operands:
                if operand.type == OpType.REGISTER:
                    if operand.value not in regs:
                        regs.append(operand.value)
            code.append(ins)
        return Program(code, headers, regs)

    @staticmethod
    def parse_file(filename: str):
        with open(filename, "r") as f:
            lines = [l.strip() for l in f]
        return Program.parse(lines)

    @staticmethod
    def parse_header(line: str):
        words = line.split()
        if len(words) < 2 or words[0] not in HEADER_TYPES:
            return None
        for header_type in HeaderType:
            if words[0].upper() == header_type.name:
                return {header_type: str.join(" ", words[1:])}
        return None

    def to_string(self, indent=0):
        return "\n".join(l.to_string(indent=indent) for l in self.code)
    
    def toColour(self, indent=0):
        return "\n".join(l.to_colour(indent=indent) for l in self.code)

def preprocess_source(source: str):

    while "  " in source:
        source = source.replace("  ", " ")
    source = strip_singleline_comments(source)
    source = strip_multiline_comments(source)

    return source

def strip_singleline_comments(source: str):
    while "//" in source:
        comment_start = source.index("//")
        comment_end = comment_start
        for char in source[comment_start:]:
            if char == "\n"[0]:
                c = char.encode("ascii")
                break
            else:
                comment_end += 1
        source = source[:comment_start] + source[comment_end:]

    return source

def strip_multiline_comments(source: str):

    while "/*" in source:
        comment_start = source.index("/*")
        comment_end = comment_start + 2
        for index in range(len(source[comment_start:])):
            if source[comment_start+index:].startswith("*/"):
                break
            else:
                comment_end += 1
        
        source = source[:comment_start] + source[comment_end:]

    return source