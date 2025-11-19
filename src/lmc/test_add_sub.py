import textwrap

import pytest

from .vm import LMC, int_reader, IntWriter
from .assembler import Assembler

@pytest.fixture
def lmc() -> LMC:
    vm = LMC()
    return vm


@pytest.fixture
def asm() -> Assembler:
    asm = Assembler()
    return asm


@pytest.mark.parametrize("a, b, total", [
    (0, 1, 1),
    (1, 0, 1),
    (1, 1, 2),
    (1, 498, 499),
    (499, 499, 998),
    (17, 4, 21),
    (20, 22, 42),
    (999, 1, 0),  # because the LMC ALU's size is only three digits
])
def test_can_add_two_unsigned_numbers(lmc: LMC, asm: Assembler, a: int, b: int, total: int) -> None:
    code = asm.run(textwrap.dedent("""
        inp
        sta a
        inp
        add a
        out
        hlt
    a   dat
    """))
    lmc.reset()
    lmc.clear()
    lmc.load(code)
    lmc.set_input(int_reader([a, b]))
    output = IntWriter()
    lmc.set_output(output.write)
    lmc.run()
    assert output.data == [total]


@pytest.mark.parametrize("a, b, difference", [
    (0, 1, -1),
    (1, 0, 1),
    (1, 1, 0),
    (1, 498, -497),
    (499, 499, 0),
    (17, 4, 13),
    (4, 17, -13),
    (20, 22, -2),
    (999, 1, -2),
])
def test_can_subtract_b_from_a(lmc: LMC, asm: Assembler, a: int, b: int, difference: int) -> None:
    code = asm.run(textwrap.dedent("""
        inp
        sta a
        inp
        sta b
        lda a
        sub b
        out
        hlt
    a   dat
    b   dat
    """))
    lmc.clear()
    lmc.reset()
    lmc.load(code)
    lmc.set_input(int_reader([a, b]))
    output = IntWriter(signed=True)
    lmc.set_output(output.write)
    lmc.run()
    assert output.data == [difference]
