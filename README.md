# Little Man Computer
## Introduction
The "[Little Man Computer](https://en.wikipedia.org/wiki/Little_Man_Computer)" 
(LMC) is a very basic model
of a [van Neumann computer](https://en.wikipedia.org/wiki/Von_Neumann_architecture), made
for education purpose. The LMC as a concept was originally created by 
[Dr. Stuart Madnick](https://en.wikipedia.org/wiki/Stuart_Madnick) 
at [MIT](https://en.wikipedia.org/wiki/Massachusetts_Institute_of_Technology) in 1965.
 
My goal when working on my LMC simulator was to practice creating a little
grammar based parser (using [lark](https://pypi.org/project/lark/)), to make a model of the
[fetch/decode/execute cycle](https://en.wikipedia.org/wiki/Instruction_cycle) 
of a CPU and to implement some fundamental CPU operations.

## Scope
My LMC simulator follows the 
[LMC definition of the Marquette University](http://www.povinelli.org/teaching/eece2710/lmc.html), 
Milwaukee, Wisconsin, USA, but
with the Mnemonics as reported by [Wikipedia](https://en.wikipedia.org/wiki/Little_Man_Computer#Instructions), 
and not the Marquette LMC mnemonics. I also did not implement Marquette's "store address".
Therefore, opcode 4 remains as "reserved".

My implementation of the LMC simulator stays decimal, but does only allow positive numbers for addresses,
RAM cells and register values. My ALU simulation uses ten's complement addition. It folds back
overflows into the including number ranges (0, 99) for addresses and (0, 999) for memory and register values.

__LMC simulator's registers__

| Name   | Meaning                      | Remark                                                                                                                      |
|--------|------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| ACC    | Accumulator                  | Changed by operations INP, LDA, ADD, SUB,<br/>and changes do affect the CPU flags                                           |
| PC     | Program Counter              | Incremented by a fetch, always points to the<br>_next_ instruction to be executed.<br>Set to a new value by BRA, BRP or BRZ |
| CIR    | Current Instruction Register | Always holds the instruction to be executed after a fetch and decode                                                        |
| MAR    | Memory Address Register      | The RAM address involved in the next memory read or write                                                                   |
| MDR    | Memory Data Register         | The value to be written to the memory cell referenced by MAR,<br>or the value most recently read from memory                |
| Z-Flag | Zero Flag                    | Set if the ACC is zero, else reset                                                                                          |
| P-Flag | Positive Flag                | Set if the ACC has a value greater or equal 500,<br>reset if 0 <= ACC < 500                                                 |

The LMC instructions support direct addressing (ADD, SUB, LDA, STA, BRA, BRP, BRZ) 
and implicit addressing (INP, OUT, HLT). Indirect addressing is not supported on CPU level.

* ADD works like ACC = (ACC + MDR) mod 1000.
* SUB works like ACC = (ACC + 1000 - MDR) mod 1000

The Z and P flags are adjusted after any opration affecting ACC.

## Programs
* The simulator core functions are in the source file [vm.py](./src/lmc/vm.py).
* There is an [assembler](./src/lmc/assembler.py) that translates LMC source files 
(.a) into LMC machine code that can directly be loaded into the simulator core.
* The assembler is based on [Lark](https://pypi.org/project/lark/). It provides support for symbolic memory 
locations and for the DAT directive. It does support an ORG directive to allow 
easy location of the code and data inside the LMC's RAM.
* An [LMC launcher](./src/lmc/lmc.py) allows to assemble and run programs.
* The launcher is based on [Typer](https://pypi.org/project/typer/). It has a run mode and an interactive mode.
Try `python lmc.py --help` to see a usage information.
The interactive mode ("trace mode") uses
[Textual](https://pypi.org/project/textual/) to create
the Terminal User Interface (TUI). The "run mode" uses [Rich](https://pypi.org/project/rich/).

## Examples
Example programs for the LMC are given in the [examples](./examples) directory.

## Dependencies
* Python 3.14.x
* Rich
* Textual
* Lark
* Typer

---