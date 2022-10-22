from enum import Enum
from enum import auto
from colorama import Fore, Back, Style
import typing

class OpType(Enum):
    REGISTER = auto()
    NUMBER = auto()
    ADDRESS = auto()
    LABEL = auto()
    PORT = auto()
    RELATIVE = auto()
    NEGATIVE = auto()
    STACKPTR = auto()
    OTHER = auto()


class Operand():
    # ======== Static variables ========

    prefixes = {
        OpType.REGISTER: "$",
        OpType.ADDRESS:  "#",
        OpType.LABEL:    ".",
        OpType.PORT:     "%",
        OpType.RELATIVE: "~",
        OpType.NEGATIVE: "-",
        OpType.OTHER:    "@",
    }
    "Gets the operand prefix ($, #, %, ...) given an OpType"

    colours = {
        OpType.REGISTER: Fore.LIGHTCYAN_EX,
        OpType.ADDRESS:  Fore.GREEN,
        OpType.LABEL:    Fore.YELLOW,
        OpType.PORT:     Fore.GREEN,
        OpType.RELATIVE: Fore.YELLOW,
        OpType.NEGATIVE: Fore.RESET,
        OpType.OTHER:    Fore.RED,
    }
    "Gets the syntax highlight color given an OpType"

    optype_from_prefix = dict((v,k) for k,v in prefixes.items())
    "Gets OpType givin an operand prefix ($, #, %, ...)"

    # === Define special parsing methods for types ===
    special_types = [
        (lambda a: a[0].isnumeric(),                          OpType.NUMBER,   lambda a:a),
        (lambda a: a[0] == "0" and a[1].isalpha(),            OpType.NUMBER,   lambda a:str(int(a,base=0))),
        (lambda a: a[0].upper() == "M",                       OpType.ADDRESS,  lambda a:a[1:]),
        (lambda a: a[0].upper() == "R",                       OpType.REGISTER, lambda a:a[1:]),
        (lambda a: a == "SP",                                 OpType.STACKPTR, lambda :"SP"),
        (lambda a: a[0] == "+",                               OpType.NEGATIVE, lambda a: f"-{a}"),
    ]
    "If special_types[n][0](operand_string) returns True, then operand_string's type is special_types[n][1]"

    def __init__(self, type=OpType.NUMBER, value="", word=0, extra:dict[str, typing.Any]={}):
        self.type = type
        "OpType.REGISTER, OpType.ADDRESS, OpType.LABEL, ..."
        self.value = value
        self.word = word
        "For multi-word processing"
        self.extra = extra
        "Any extra information that may need to be stored"
        self.type_class = self.get_type_class()

    # ======== Static methods ========
    @staticmethod
    def parse(operand: str) -> "Operand":
        "Expects a clean input, no whitespace shenanigans"
        # Get the operand type
        t: "OpType | None" = Operand.optype_from_prefix.get(operand[0])
        opr = None
        if t is None:
            for sp_type in Operand.special_types:
                try:
                    if sp_type[0](operand):
                        t = sp_type[1]
                        opr = sp_type[2](operand)
                except:
                    continue
        else:
            if t in Operand.prefixes.keys():
                opr = operand[1:]
        if not t or not opr:
            raise ValueError(f"Cannot parse operand '{operand}', unknown type.")

        # Get word (for multiword code)
        if opr[-1] == "]" and "[" in opr:
            word = int(opr.split("[")[1][:-1])
        else:
            word = 0
        return Operand(t, opr, word)

    # ======== Operand methods ========

    def get_type_class(self) -> str:
        "Uses self.type and self.value to generate a UTRX parameter type string, see UTRX_syntax.txt"
        type_class = "A"
        if self.type in [OpType.REGISTER]:
            type_class += "R"
            if self.value == "0" and self.type == OpType.REGISTER:
                type_class += "Z"
            if self.value == "SP":
                type_class += "SP"
            if self.value.isnumeric():
                type_class += "G"
        else:
            type_class += "I"
            if self.value == "0" and self.type == OpType.NUMBER:
                type_class += "Z"
            if self.type == OpType.NEGATIVE:
                type_class += "C"
            if self.type == OpType.ADDRESS:
                type_class += "M"
            if self.type == OpType.LABEL:
                type_class += "L"
            if self.type == OpType.PORT:
                type_class += "O"
        return type_class

    def prefix(self) -> str:
        return Operand.prefixes.get(self.type, "")

    def __str__(self):
        out = f"{self.prefix()}{self.value}"
        if self.word: out += f"[{self.word}]"
        return out

    def to_colour(self) -> str:
        out = f"{Operand.colours.get(self.type, Fore.RESET)}{self.prefix()}{self.value}{Style.RESET_ALL}"
        if self.word: out += f"[{self.word}]"
        return out
