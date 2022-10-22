from typing import TYPE_CHECKING
from urclToISA.operand import Operand 

class Block():
    "a section of URCL code, good for printing"
    def __init__(self, URCL_labels:list[Operand]=[], code:list[str]=[]):
        self.URCL_labels = URCL_labels
        self.code = code
    
    def to_string(self, indent=0):
        out = f"{'' if not self.URCL_labels else ' '.join([str(label) for label in self.URCL_labels]):>{indent}} | "
        out += f"\n{'':>{indent}} | ".join(ln for ln in self.code)
        return out
    
    def print(self, indent=0):
        print(self.to_string(indent=indent))