import argparse
from lark import Lark, Transformer, Token, Tree, UnexpectedInput


def get_cli_args() -> argparse.Namespace:
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "a_file",
        metavar="LMC_SOURCE",
        help="LMC source file",
    )
    return argparser.parse_args()


grammar = r"""
?start: _instruction? (_NL _instruction)* _NL*

_NL: NEWLINE
COMMENT: _COMMENT_STR (_NL _COMMENT_STR)*
_COMMENT_STR: /\s*(#|\/\/)[^\n]*/+

_instruction: labeldef? op

?op: ("hlt"i | "cob"i) -> hlt
    | "add"i (label | addr) -> add
    | "sub"i (label | addr) -> sub
    | "sta"i (label | addr) -> sta
    | "lda"i (label | addr) -> lda
    | "bra"i (label | addr) -> bra
    | "brz"i (label | addr) -> brz
    | "brp"i (label | addr) -> brp
    | "inp"i -> inp
    | "out"i -> out
    | "dat"i value -> dat
    | "org"i addr -> org

?addr: ADDR
?value: [SIGNED_NUMBER]
?label: LABEL
labeldef: LABEL -> labeldef

LABEL: /[a-zA-Z_][_a-zA-Z0-9]*/
ADDR: /0/ | /[1-9][0-9]/

%import common.NEWLINE
%import common.WS_INLINE
%import common.SH_COMMENT
%import common.SIGNED_NUMBER

%ignore WS_INLINE
%ignore COMMENT
"""


class Assembler(Transformer):
    labels: dict[str, int]
    location: int
    memory: list[tuple[int, int | tuple[int, int | str]]]

    def __init__(self):
        super().__init__()
        self._parser = Lark(grammar, parser="lalr", transformer=self)
        self.reset()

    def reset(self) -> None:
        self.labels = {}
        self.memory = []
        self.location = 0

    def start(self, lines: list[Tree]) -> list[tuple[int, int]]:
        for tree in lines:
            match tree:
                case Tree("labeldef", [addr]):
                    self.labels[addr.value.lower()] = self.location
                case Tree("org", [addr]):
                    self.location = addr.value
                case Tree("dat", [item]):
                    value = 0 if item is None else item.value
                    if not -999 <= value <= 999:
                        raise UnexpectedInput(
                            f"[red]Value {value} out of range [-999 ... +999] "
                            f"at line {item.line}, column {item.column}[/]"
                        )
                    self.memory.append((self.location, value))
                    self.location += 1
                case Tree("hlt", _):
                    self.memory.append((self.location, 0))
                    self.location += 1
                case Tree("add", [addr]):
                    self.memory.append((self.location, (100, addr.value)))
                    self.location += 1
                case Tree("sub", [addr]):
                    self.memory.append((self.location, (200, addr.value)))
                    self.location += 1
                case Tree("sta", [addr]):
                    self.memory.append((self.location, (300, addr.value)))
                    self.location += 1
                case Tree("lda", [addr]):
                    self.memory.append((self.location, (500, addr.value)))
                    self.location += 1
                case Tree("bra", [addr]):
                    self.memory.append((self.location, (600, addr.value)))
                    self.location += 1
                case Tree("brz", [addr]):
                    self.memory.append((self.location, (700, addr.value)))
                    self.location += 1
                case Tree("brp", [addr]):
                    self.memory.append((self.location, (800, addr.value)))
                    self.location += 1
                case Tree("inp", _):
                    self.memory.append((self.location, 901))
                    self.location += 1
                case Tree("out", _):
                    self.memory.append((self.location, 902))
                    self.location += 1
        for index, item in enumerate(self.memory):
            if isinstance(item[1], tuple):
                location, (opcode, label) = item
                addr = opcode + int(self.labels.get(str(label).lower(), label))
                self.memory[index] = (location, addr)
        return self.memory

    @staticmethod
    def ADDR(token: Token) -> Token:
        token.value = int(token.value)
        return token

    @staticmethod
    def SIGNED_NUMBER(token: Token) -> Token:
        token.value = int(token.value)
        return token

    def run(self, src: str):
        self.reset()
        return self._parser.parse(src)
