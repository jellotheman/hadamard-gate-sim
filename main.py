# a small program to show what a hadamard gate does to one quantum bit

#aviyansh
import math
import random

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


SQRT_2 = math.sqrt(2)
console = Console(markup=False, highlight=False)
# each state holds 2 numbers called amplitudes, one for 0 and one for 1
# their squared sizes give the chances of measuring each result
State = tuple[complex, complex]
STATES = {
    "1": ("|0>", (1.0, 0.0)),
    "2": ("|1>", (0.0, 1.0)),
    "3": ("|+>", (1 / SQRT_2, 1 / SQRT_2)),
    "4": ("|->", (1 / SQRT_2, -1 / SQRT_2)),
}


def hadamard(state: State) -> State:
    # add and subtract the input amplitudes, then divide each by the square root of 2
    # this calculates the new state; measuring it happens later
    a, b = state
    return (a + b) / SQRT_2, (a - b) / SQRT_2


def format_amplitude(value: complex) -> str:
    # show 4 decimal places and turn tiny leftover values into 0 for display
    real = 0.0 if abs(value.real) < 0.00005 else value.real
    imag = 0.0 if abs(value.imag) < 0.00005 else value.imag
    if imag == 0:
        return f"{real:.4f}"
    return f"({real:.4f}{imag:+.4f}j)"


def format_state(state: State) -> str:
    # write the state as text, keeping a negative second amplitude easy to read
    a, b = state
    if b.imag == 0 and b.real < 0:
        return f"{format_amplitude(a)}|0> - {format_amplitude(-b)}|1>"
    return f"{format_amplitude(a)}|0> + {format_amplitude(b)}|1>"

# sreeram
def normalize(state: State) -> State:
    # resize the amplitudes so the chances add up to 1, meaning 100 percent
    # infinity, undefined numbers and a pair of zeros cannot make a valid state
    components = [part for a in state for part in (a.real, a.imag)]
    if not all(math.isfinite(part) for part in components):
        raise ValueError("Amplitudes must be finite numbers.")
    scale = max(abs(part) for part in components)
    if scale == 0:
        raise ValueError("Both amplitudes cannot be zero.")
    # resize both by the same amount first so huge or tiny numbers are easier to handle
    a, b = (amplitude / scale for amplitude in state)
    norm = math.hypot(abs(a), abs(b))
    return a / norm, b / norm

# alicia
def read_custom_state() -> State:
    # ask for 2 amplitudes and try again if the numbers cannot make a valid state
    console.print("\nEnter real numbers (e.g. 0.6) or complex numbers (e.g. 0.5+0.5j).")
    console.print("Here j is the imaginary unit, with j*j = -1.", style="dim")
    console.print("The amplitudes will be normalized so |a|^2 + |b|^2 = 1.")
    while True:
        try:
            a = complex(input("  Amplitude a for |0>: ").strip())
            b = complex(input("  Amplitude b for |1>: ").strip())
        except ValueError:
            console.print("  Enter numbers like 0.6, -0.8, or 0.5+0.5j (no expressions).", style="yellow")
            continue
        try:
            state = normalize((a, b))
        except ValueError as error:
            console.print(f"  {error}", style="yellow")
            continue
        console.print(f"  Normalized input: {format_state(state)}", style="green")
        return state


def measure(state: State, shots: int) -> tuple[int, int]:
    # the input's chances must already add up to 1 before this is called
    # each shot is a fresh try at measuring the same prepared state as 0 or 1
    # send back the number of zeros and ones
    if shots < 1:
        raise ValueError("The number of shots must be positive.")
    # keep the chance between 0 and 1 in case computer rounding puts it just outside
    probability_zero = min(1.0, max(0.0, abs(state[0]) ** 2))
    # pick a random number from 0 up to, but not including, 1 for each shot
    # count a zero if it is below the chance of zero; otherwise count a one
    # adding the true/false results counts how many times zero was picked
    zeros = sum(random.random() < probability_zero for _ in range(shots))
    return zeros, shots - zeros

# hitanshi
def read_shots() -> int:
    # ask how many measurements to try, from 1 to 100000; enter alone uses 1000
    while True:
        answer = input("\nMeasurement shots [1000] (1-100000): ").strip()
        if not answer:
            return 1000
        try:
            shots = int(answer)
        except ValueError:
            console.print("  Please enter a whole number, such as 1000.", style="yellow")
            continue
        if 1 <= shots <= 100000:
            return shots
        console.print("  Please enter a number from 1 to 100000.", style="yellow")


def probability_bar(probability: float) -> Text:
    # turn a chance between 0 and 1 into a small bar and a percentage
    filled = round(probability * 16)
    bar = Text("#" * filled, style="cyan")
    bar.append("-" * (16 - filled), style="dim")
    bar.append(f" {probability:.2%}")
    return bar


def show_probabilities(initial: State, result: State, gate: str = "H") -> None:
    # compare the chances of 0 and 1 before and after applying the gate
    table = Table(box=box.SIMPLE_HEAD, header_style="bold cyan")
    table.add_column("Outcome")
    table.add_column(f"Before {gate}")
    table.add_column(f"After {gate}")
    for bit in range(2):
        before = min(1.0, abs(initial[bit]) ** 2)
        after = min(1.0, abs(result[bit]) ** 2)
        table.add_row(f"|{bit}>", probability_bar(before), probability_bar(after))
    console.print(table)

# vedika
def run() -> None:
    # let the user pick a state, see the calculation and try measurements until they quit
    console.print()
    console.print(Panel(
        Text("HADAMARD QUANTUM GATE SIMULATOR\n\n"
             "A single qubit has state a|0> + b|1>.\n"
             "Probabilities are |a|^2 and |b|^2; together they add to 1."),
        border_style="cyan", padding=(1, 2),
    ))

    while True:
        console.print("\n[1 / INPUT] Choose a starting state", style="bold cyan")
        menu = Table(box=box.SIMPLE_HEAD, header_style="bold", padding=(0, 1))
        menu.add_column("Key", style="cyan")
        menu.add_column("State")
        menu.add_column("Amplitudes (a, b)")
        menu.add_row("1", "|0>", "1, 0")
        menu.add_row("2", "|1>", "0, 1")
        menu.add_row("3", "|+>", "1/sqrt(2), 1/sqrt(2)")
        menu.add_row("4", "|->", "1/sqrt(2), -1/sqrt(2)")
        menu.add_row("5", "Custom", "Enter real or complex amplitudes")
        menu.add_row("Q", "Quit", "")
        console.print(menu)
        choice = input("\nYour choice [1-5 / Q]: ").strip().lower()
        if choice == "q":
            console.print("\nSimulation finished. Goodbye!", style="cyan")
            return
        if choice not in STATES and choice != "5":
            console.print("  Please choose 1, 2, 3, 4, 5, or Q.", style="yellow")
            continue
# sreeram
        if choice == "5":
            name, initial = "|psi>", read_custom_state()
        else:
            name, initial = STATES[choice]
        result = hadamard(initial)
        console.print("\n[2 / PROCESSING] Apply the Hadamard gate", style="bold cyan")
        console.print(Panel(Text(
            f"{name} ----[ H ]---- output\n\n"
            "H = 1/sqrt(2) * [ 1   1 ]\n"
            "                [ 1  -1 ]\n\n"
            "New amplitudes: ((a + b)/sqrt(2), (a - b)/sqrt(2))\n\n"
            f"Input:  {format_state(initial)}\n"
            f"Output: {format_state(result)}"
        ), border_style="blue", title="Gate calculation"))

        console.print("\n[3 / OUTPUT] Theoretical measurement probabilities", style="bold cyan")
        show_probabilities(initial, result)
        restored = hadamard(result)
        console.print(Panel(Text(
            f"Apply H again (before measuring):\n{format_state(restored)}\n\n"
            "H applied twice restores the input: H * H = I."
        ), title="Reversibility", border_style="green"))
        console.print("\nEach shot prepares the input again, applies H, then measures.", style="dim")
        shots = read_shots()
        zeros, ones = measure(result, shots)
        console.print(f"\nSimulated measurements ({shots:,} shots)", style="bold green")
        samples = Table(box=box.SIMPLE_HEAD, header_style="bold green")
        for heading in ("Outcome", "Count", "Observed", "Expected"):
            samples.add_column(heading, justify="left" if heading == "Outcome" else "right")
        for bit, count in enumerate((zeros, ones)):
            samples.add_row(f"|{bit}>", f"{count:,}", f"{count / shots:.2%}",
                            f"{min(1.0, abs(result[bit]) ** 2):.2%}")
        console.print(samples)
        console.print("Random samples may differ from the theoretical probabilities.", style="dim")
        console.rule(characters="-", style="dim")


def main() -> None:
    # start the program and exit without an error screen if input stops or ctrl+c is pressed
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        console.print("\nSimulation finished. Goodbye!", style="cyan")


if __name__ == "__main__":
    main()
