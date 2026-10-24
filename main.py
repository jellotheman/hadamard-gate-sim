"""A small, interactive single-qubit Hadamard gate simulator."""

import math
import random

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


SQRT_2 = math.sqrt(2)
console = Console(markup=False, highlight=False)
State = tuple[complex, complex]
STATES = {
    "1": ("|0>", (1.0, 0.0)),
    "2": ("|1>", (0.0, 1.0)),
    "3": ("|+>", (1 / SQRT_2, 1 / SQRT_2)),
    "4": ("|->", (1 / SQRT_2, -1 / SQRT_2)),
}


def hadamard(state: State) -> State:
    """Apply H to amplitudes (a, b), returning ((a+b), (a-b))/sqrt(2)."""
    a, b = state
    return (a + b) / SQRT_2, (a - b) / SQRT_2


def format_amplitude(value: complex) -> str:
    """Display real or complex amplitudes to four decimal places."""
    real = 0.0 if abs(value.real) < 0.00005 else value.real
    imag = 0.0 if abs(value.imag) < 0.00005 else value.imag
    if imag == 0:
        return f"{real:.4f}"
    return f"({real:.4f}{imag:+.4f}j)"


def format_state(state: State) -> str:
    """Keep the relative sign visible and suppress distracting negative zeros."""
    a, b = state
    if b.imag == 0 and b.real < 0:
        return f"{format_amplitude(a)}|0> - {format_amplitude(-b)}|1>"
    return f"{format_amplitude(a)}|0> + {format_amplitude(b)}|1>"


def normalize(state: State) -> State:
    """Normalize finite, nonzero amplitudes, including very large/small inputs."""
    components = [part for a in state for part in (a.real, a.imag)]
    if not all(math.isfinite(part) for part in components):
        raise ValueError("Amplitudes must be finite numbers.")
    scale = max(abs(part) for part in components)
    if scale == 0:
        raise ValueError("Both amplitudes cannot be zero.")
    a, b = (amplitude / scale for amplitude in state)
    norm = math.hypot(abs(a), abs(b))
    return a / norm, b / norm


def read_custom_state() -> State:
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
    """Measure freshly prepared copies of a normalized state in the Z basis."""
    if shots < 1:
        raise ValueError("The number of shots must be positive.")
    probability_zero = min(1.0, max(0.0, abs(state[0]) ** 2))
    zeros = sum(random.random() < probability_zero for _ in range(shots))
    return zeros, shots - zeros


def read_shots() -> int:
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
    filled = round(probability * 16)
    bar = Text("#" * filled, style="cyan")
    bar.append("-" * (16 - filled), style="dim")
    bar.append(f" {probability:.2%}")
    return bar


def show_probabilities(initial: State, result: State) -> None:
    table = Table(box=box.SIMPLE_HEAD, header_style="bold cyan")
    table.add_column("Outcome")
    table.add_column("Before H")
    table.add_column("After H")
    for bit in range(2):
        before = min(1.0, abs(initial[bit]) ** 2)
        after = min(1.0, abs(result[bit]) ** 2)
        table.add_row(f"|{bit}>", probability_bar(before), probability_bar(after))
    console.print(table)


def run() -> None:
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
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        console.print("\nSimulation finished. Goodbye!", style="cyan")


if __name__ == "__main__":
    main()
