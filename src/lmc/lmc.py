from pathlib import Path
from typing import Annotated

import rich
import typer
from rich.syntax import Syntax
from rich.text import Text
from textual.app import App, ComposeResult, RenderResult
from textual.containers import ScrollableContainer
from textual.binding import Binding
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Header, Footer, Static

from .assembler import Assembler
from .vm import LMC, int_reader, IntWriter

app = typer.Typer(
    help="Run an LMC program.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command(help="Assemble, load and run a given LMC program")
def run(
        prog: Annotated[Path, typer.Argument(
            exists=True, help="The LMC assembler program to be run")],
        inp: Annotated[list[int], typer.Argument(
            min=-500, max=499, help="Run with a list of input numbers")] = None,
        signed: Annotated[bool, typer.Option(
            "--signed/--unsigne", help="Signed output (default: unsigned numbers)")] = False) -> None:

    asm = Assembler()
    code = asm.run(prog.read_text())
    vm = LMC()
    vm.load(code)
    vm.set_input(int_reader(inp))
    output = IntWriter(signed=signed)
    vm.set_output(output.write)
    vm.run()
    if vm.run_state == "abort":
        rich.print("Error:", vm.error)
    else:
        rich.print("OK", output)


class CodeView(Widget):
    """Widget to display Python code."""

    code = reactive("")

    def render(self) -> RenderResult:
        # Syntax is a Rich renderable that displays syntax highlighted code
        syntax = Syntax(self.code, "c-objdump", line_numbers=True, indent_guides=True)
        return syntax


class ScreenApp(App):
    TITLE = "LMC"
    SUB_TITLE = "The Little Man Computer"

    BINDINGS = [
        Binding("s", "step", "Step"),
        Binding("q", "quit", "Quit", priority=True),
    ]

    DEFAULT_CSS = """
    .box { width: 1fr; }
    """

    def __init__(self, prog: Path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.vm = LMC()
        asm = Assembler()
        code = asm.run(prog.read_text())
        self.vm.load(code)
        self.reg_view = Static(Text(str(self.vm)), classes="box")

    def action_step(self) -> None:
        self.vm.single_step()

    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            self.reg_view
        )
        yield Footer()


@app.command(help="Assemble, load and interactively step through a given LMC program")
def trace(prog: Path) -> None:
    visual_app = ScreenApp(prog)
    visual_app.sub_title = str(prog.absolute())
    visual_app.run()


if __name__ == "__main__":
    app()
