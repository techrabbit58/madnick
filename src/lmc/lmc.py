from pathlib import Path
from typing import Annotated, Optional

import rich
import typer

from .vm import LMC, int_reader, Console, IntWriter
from .assembler import asm

app = typer.Typer(
    help="Run an LMC program.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command(help="Assemble, load and run a given LMC program")
def run(
        prog: Annotated[Path, typer.Argument(exists=True, help="The LMC assembler program to be run")],
        inp: Annotated[list[int], typer.Argument(min=-500, max=499)] = None) -> None:

    rich.print(f"[bold yellow]run[/] [cyan]{prog}[/]"
               f" {f'with input {inp}' if inp is not None else 'without input'} ...")

    if not inp:
        inp = []
    code = asm(prog.read_text())
    vm = LMC()
    vm.load(code)
    vm.set_input(int_reader(*inp))
    output = IntWriter()
    vm.set_output(output.write)
    vm.run()
    rich.print(vm)
    rich.print(output)



@app.command(help="Assemble, load and interactively step through a given LMC program")
def trace(prog: Path) -> None:

    rich.print(f"[bold yellow]trace[/] [cyan]{prog}[/] visually ...")


if __name__ == "__main__":
    app()
