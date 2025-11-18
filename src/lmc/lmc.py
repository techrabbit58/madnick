from pathlib import Path
from typing import Annotated, Optional

import rich
import typer

from .vm import LMC, card_input, Console
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

    code = asm(prog.read_text())
    vm = LMC()
    vm.load(code)
    vm.set_input(card_input(*inp))
    console = Console()
    vm.set_output(console.output)
    vm.run()
    rich.print(vm)
    rich.print(console)



@app.command(help="Assemble, load and interactively step through a given LMC program")
def trace(prog: Path) -> None:

    rich.print(f"[bold yellow]trace[/] [cyan]{prog}[/] visually ...")


if __name__ == "__main__":
    app()
