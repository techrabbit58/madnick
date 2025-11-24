import io
from collections.abc import Callable, Iterable


def tens_complement(value: int, base: int = 1000) -> int:
    return base + value if value < 0 else value


def to_signed(value: int, base: int = 1000) -> int:
    sign = 1
    if value >= base // 2:
        value = base - value
        sign = -1
    return sign * value


def disassemble(op: int, addr: int) -> str:
    match op, addr:
        case (0, _):
            return "HLT"
        case (1, addr):
            return f"ADD {addr}"
        case (2, addr):
            return f"SUB {addr}"
        case (3, addr):
            return f"STA {addr}"
        case (5, addr):
            return f"LDA {addr}"
        case (6, addr):
            return f"BRZ {addr}"
        case (7, addr):
            return f"BRP {addr}"
        case (8, addr):
            return f"BRA {addr}"
        case (9, 1):
            return "INP"
        case (9, 2):
            return "OUT"
        case None:
            return "no instruction"
        case _:
            return f"undefined {op, addr}"


def int_reader(cards: Iterable[int]) -> Callable[[], int]:
    card = iter(cards) if cards is not None else iter([])

    def int_provider() -> int | None:
        try:
            return tens_complement(next(card))
        except StopIteration:
            return None

    return int_provider


class IntWriter:
    def __init__(self, *, base: int = 1000, signed: bool = False, sep: str = ", ") -> None:
        self._cards: list[int] = []
        self.base = base
        self.signed = signed
        self.separator = sep

    def reset(self) -> None:
        self._cards.clear()

    def write(self, value: int) -> None:
        if self.signed:
            value = to_signed(value, self.base)
        self._cards.append(value)

    @property
    def data(self) -> list[int]:
        return self._cards.copy()

    def __str__(self) -> str:
        return self.separator.join(map(str, self._cards))


class LMC:
    MEMSIZE = 100  # LMC memory size is 100 words
    BASE = 1000  # works only with tens complement numbers 0..999
    _error: str | None
    _is_terminated: bool
    _read_input: Callable[[], int]
    _write_output: Callable[[int], None]
    pc: int  # program counter (PC)
    acc: int  # accumulator (ACC)
    mar: int  # memory address register (MAR)
    mdr: int  # memory data register (MDR)
    cir: tuple[int, int]  # current instruction register (CIR)
    is_zero: bool
    is_nonnegative: bool
    carry: int

    def __init__(self) -> None:
        self.mem = [0] * self.MEMSIZE
        self.reset()

    def set_input(self, func: Callable[[], int]) -> None:
        self._read_input = func

    def set_output(self, func: Callable[[int], None]) -> None:
        self._write_output = func

    def reset(self) -> None:
        self.pc = 0
        self.acc = 0
        self.mar = 0
        self.mdr = 0
        self.cir = 0, 0
        self.carry = 1
        self._set_flags()
        self._is_terminated = False
        self._error = None

    def clear(self) -> None:
        for i in range(len(self.mem)):
            self.mem[i] = 0
        self.reset()

    def load(self, program: list[tuple[int, int]]) -> None:
        for self.mar, self.mdr in program:
            self._write_mem()
        self.reset()

    @property
    def error(self) -> str | None:
        return self._error

    def _write_mem(self) -> None:
        self.mem[self.mar] = self.mdr

    def _read_mem(self) -> None:
        self.mdr = self.mem[self.mar]

    def _set_flags(self) -> None:
        self.is_zero = self.acc == 0
        self.is_nonnegative = self.acc < self.BASE // 2

    def fetch(self) -> None:
        self.mar = self.pc
        self.mdr = self.mem[self.mar]
        self.pc += 1

    def decode(self) -> None:
        self.cir = divmod(self.mdr, self.MEMSIZE)
        self.mar = self.cir[1]
        self._read_mem()

    def execute(self) -> None:
        match self.cir[0]:
            case 0:  # HLT
                self._is_terminated = True
            case 1:  # ADD addr
                self.acc += self.mdr
            case 2:  # SUB addr
                self.acc += self.BASE - self.mdr
            case 3:  # STA addr
                self.mdr = self.acc
                self._write_mem()
            case 5:  # LDA addr
                self.acc = self.mdr
            case 6:  # BRA addr
                self.pc = self.mar
            case 7:  # BRZ addr
                if self.is_zero:
                    self.pc = self.mar
            case 8:  # BRP addr
                if self.is_nonnegative:
                    self.pc = self.mar
            case 9 if self.cir[1] == 1:  # INP
                n = self._read_input()
                if n is None:
                    self._error = f"End of input file"
                    self._is_terminated = True
                    return
                if not 0 <= n < self.BASE:
                    self._error = f"Input out of range (0..{self.BASE - 1}): {n}"
                    self._is_terminated = True
                    return
                self.acc = n
            case 9 if self.cir[1] == 2:  # OUT
                self._write_output(self.acc)
            case _:
                self._error = f"Bad instruction {self.cir}"
                self._is_terminated = True
        self.carry = self.acc // self.BASE
        self.acc %= self.BASE
        self._set_flags()

    def single_step(self) -> None:
        if self.run_state == "run":
            self.fetch()
            self.decode()
            self.execute()

    @property
    def run_state(self) -> str:
        if not self._is_terminated:
            return "run"
        elif self._error:
            return "abort"
        else:
            return "halt"

    def run(self) -> None:
        while True:
            self.single_step()
            if self.run_state != "run":
                break

    @property
    def memory(self) -> str:
        sb = io.StringIO()
        print("MEMORY   0     1     2     3     4     5     6     7     8     9", file=sb)
        print(f"-----{'------' * 10}", file=sb)
        for i in range(0, self.MEMSIZE, 10):
            print(f"{i:3}: ", end="", file=sb)
            for j in range(10):
                print(f" {self.mem[i + j]:5}", end="", file=sb)
            print(file=sb)
        print(f"-----{'------' * 10}", file=sb)
        print(f"        Current instruction: {disassemble(*self.cir)}", file=sb)
        return sb.getvalue()

    def __str__(self) -> str:
        sb = io.StringIO()
        print("MEMORY   0     1     2     3     4     5     6     7     8     9", file=sb)
        print(f"-----{'------' * 10}", file=sb)
        for i in range(0, self.MEMSIZE, 10):
            print(f"{i:3}: ", end="", file=sb)
            for j in range(10):
                print(f" {self.mem[i + j]:5}", end="", file=sb)
            print(file=sb)
        print(f"-----{'------' * 10}", file=sb)
        # print(f"ACC={self.acc}, MAR={self.mar}, MDR={self.mdr}, ", file=sb, end="")
        # print(f"CIR={disassemble(*self.cir)}, PC={self.pc}, RS={self.run_state}", file=sb)
        # print(f"Flags: Z={int(self.is_zero)}, P={int(self.is_nonnegative)}, ", end="", file=sb)
        # print(f"E={int(self.error is not None)}", file=sb)
        # print(f"Error: {self._error}", file=sb)
        return sb.getvalue()
