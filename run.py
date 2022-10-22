# ┌───────────────────────────────────────────────────────────────────────────┐
# │ Usage: Create a folder 'lang' containing your ISA translation file (.utrx)│
# │        Create a folder 'prog' containing your URCL code file (.urcl)      │
# │        Run the following command with your chosen file names:             │
# │ python3 run.py -f prog/code.urcl -t lang/isa.utrx                         │
# │        Or if you want to translate to core URCL use the 'core' ISA:       │
# | python3 run.py -f prog/code.urcl -t lang/core.utrx                        │
# └───────────────────────────────────────────────────────────────────────────┘

# ┌───────────────────────────────────────────────────────────────────────────┐
# | And of course remember that this is a prototype and is not finished. :)   |
# └───────────────────────────────────────────────────────────────────────────┘

from urclToISA.program import HeaderType, preprocess_source
from urclToISA.translator import Translator
from urclToISA.UTRX import Translation
import urclToISA.UTRX


def main():
    from urclToISA.program import Program
    from urclToISA.translator import Translator
    from urclToISA.isa import Block
    import colorama
    from timeit import default_timer as timer
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("-f", "--File", help="URCL file to be translated")
    p.add_argument("-t", "--Target", help="UTRX file containing translations")
    p.add_argument("-o", "--Output", help="File to store output in")
    p.add_argument("-s", "--Silent", help="Hide terminal output")
    p.add_argument("-b", "--Boring", help="Give uncoloured output")

    argv = p.parse_args()

    colorama.init(autoreset=True)
    filename = "mycode.urcl"
    if argv.File:
        filename = argv.File
    ISAtranslations = "core.utrx"
    if argv.Target:
        ISAtranslations = argv.Target

    URCLtranslations = "urclToISA/urcl.utrx"

    start = timer()

    main = Program.parse_file(filename)
    translator = Translator.from_file(URCLtranslations)
    translatorISA = Translator.from_file(ISAtranslations)

    def translate(program: Program, trans: Translator):
        done = False
        while not done:
            done = True
            for l,ins in enumerate(program.code):
                sub = trans.substitute_urcl(ins)
                if sub:
                    while len(set(sub.regs + program.regs)) != len(sub.regs + program.regs):
                        sub.prime_regs()
                    sub.unpack_placeholders()
                    sub = translate(sub, trans)
                    program.insert_sub(sub, l)
                    done = False
                    break
        return program

    def translateISA(program: Program, trans: Translator):
        out: list[Block] = []
        for l,ins in enumerate(program.code):
            out.append(Block(ins.labels, trans.substitute(ins)))
        return out

    main = translate(main, translator)

    main.make_regs_numeric()
    main.relatives_to_labels()

    end = timer()

    if not argv.Silent:
        print(f"-"*30)
        print(f"{filename} translated to {URCLtranslations}:")
        print(f"-"*30)
        if argv.Boring:
            print(main.to_string(indent=20))
        else:
            print(main.toColour(indent=20))
        print(f"-"*30)
        print(f"In {end-start:.10f} seconds.")
        print(f"Registers used: {len(main.regs)}")
        print(f"-"*30)

    start = timer()
    out = translateISA(main, translatorISA)
    end = timer()

    if not argv.Silent:
        print(f"-"*30)
        print(f"{filename} translated to {ISAtranslations}:")
        print(f"-"*30)
        for block in out:
            block.print(indent=20)
        print(f"-"*30)
        print(f"In {end-start:.10f} seconds.")
        print(f"-"*30)

    if argv.Output:
        with open(argv.Output, "w+") as f:
            for block in out:
                f.write(block.to_string() + "\n")

if __name__ == "__main__":
    main()
    #import unittest
    #unittest.main("tests.test")