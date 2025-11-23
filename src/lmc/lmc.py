from pathlib import Path
from typing import Annotated

import rich
import typer
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Digits

from .assembler import Assembler
from .vm import LMC, int_reader, IntWriter, disassemble

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


class BoxedDigits(Digits):
    def __init__(self, title: str, *args, **kwargs) -> None:
        super().__init__(*args, id=title, **kwargs)
        self.border_title = title.upper()


class Register(BoxedDigits):
    def update(self, value: int) -> None:
        super().update(f"{value:03d}")


class CurrentInstruction(BoxedDigits):
    def update(self, instruction: tuple[int, int]) -> None:
        opcode, addr = instruction
        opname, *_ = disassemble(opcode, addr).split()
        super().update(f"{opcode} {addr:02d}")


class BoxedStatic(Static):
    def __init__(self, title: str, *args, **kwargs) -> None:
        super().__init__(*args, id=title, **kwargs)
        self.border_title = title.upper()


class ScreenApp(App):
    TITLE = "LMC"
    SUB_TITLE = "The Little Man Computer"

    BINDINGS = [
        Binding("r", "reset", "Reset"),
        Binding("s", "step", "Step"),
        Binding("x", "execute", "Execute"),
        Binding("q", "quit", "Quit", priority=True),
    ]

    DEFAULT_CSS = """
    .registerbox { width: auto; margin: 1 1; }
    .memorybox { width: 1fr; height: 1fr; margin: 1 1 0 0; }
    .outputbox { width: auto; height: 1fr; margin: 1 0 0 0; }
    .flagsbox { width: 1fr; height: 3; margin: 0 1 0 0; }
    .inputbox { width: 1fr; height: 3; margin: 0 1 0 0; }
    .register { border: solid; text-align: right; width: 20; padding: 0 1 0 0; }
    .output { border: solid; text-align: center; width: 13; height: 1fr; padding: 0 1; }
    .narrowbox { border: solid; padding: 0 1; text-align: center; height: 1fr; width: 12; }
    .widebox { border: solid; padding: 0 1; height: 1fr; width: 1fr; }
    .centered-wide { border: solid; padding: 0 1; height: 1fr; width: 1fr; text-align: center; }
    """

    def __init__(self, prog: Path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.vm = LMC()
        asm = Assembler()
        code = asm.run(prog.read_text())
        self.vm.load(code)
        self.out = IntWriter()
        self.vm.set_output(self.out.write)
        self.vm.set_input(int_reader([5]))  # TODO: this is not an appropriate solution for the input

    def update_widgets(self) -> None:
        for reg in ("pc", "acc", "cir", "mar", "mdr"):
            if reg == "cir":
                self.get_widget_by_id(reg, CurrentInstruction).update(getattr(self.vm, reg))
            else:
                self.get_widget_by_id(reg, Register).update(getattr(self.vm, reg))
        self.get_widget_by_id("memory", Static).update(self.vm.memory)
        self.get_widget_by_id("z-flag", BoxedStatic).update(str(self.vm.is_zero))
        self.get_widget_by_id("p-flag", BoxedStatic).update(str(self.vm.is_nonnegative))
        self.get_widget_by_id("error", BoxedStatic).update(str(self.vm.error))
        self.get_widget_by_id("output", BoxedStatic).update(str(self.out))

    async def _ready(self) -> None:
        self.update_widgets()

    def action_reset(self) -> None:
        self.vm.reset()
        self.out.reset()
        self.update_widgets()
        self.refresh()

    def action_step(self) -> None:
        # TODO: does not yet recognize the HLT state
        self.vm.single_step()
        self.update_widgets()
        self.refresh()

    def action_execute(self) -> None:
        # TODO: action needs to be defined
        self.update_widgets()
        self.refresh()

    def compose(self) -> ComposeResult:
        # TODO: indicator for the run state is missing
        # TODO: input contol is missing
        # TODO: output needs to be newline separated, not comma separated
        yield Header()
        yield Vertical(
            Horizontal(
                Vertical(
                    Register("pc", classes="register"),
                    Register("acc", classes="register"),
                    CurrentInstruction("cir", classes="register"),
                    Register("mar", classes="register"),
                    Register("mdr", classes="register"),
                    classes="registerbox"
                ),
                Vertical(
                    Horizontal(
                        Vertical(
                            Static("", id="memory", classes="centered-wide"),
                            classes="memorybox"
                        ),
                        Vertical(
                            BoxedStatic("output", classes="output"),
                            classes="outputbox"
                        )
                    ),
                    Horizontal(
                        BoxedStatic("z-flag", classes="narrowbox"),
                        BoxedStatic("p-flag", classes="narrowbox"),
                        BoxedStatic("error", classes="widebox"),
                        classes="flagsbox"
                    ),
                    Vertical(
                        Static("Inputs...", classes="widebox"),
                        classes="inputbox"
                    )
                )
            ),
        )
        yield Footer()


@app.command(help="Assemble, load and interactively step through a given LMC program")
def trace(prog: Path) -> None:
    visual_app = ScreenApp(prog)
    visual_app.sub_title = str(prog.absolute())
    visual_app.run()


if __name__ == "__main__":
    app()
