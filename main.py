"""Explore single-qubit gates and the H-then-CNOT Bell circuit in one program."""

# START AVIYANSH #
import math
import random

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

SQRT_2 = math.sqrt(2)
SINGLE_LABELS = ("0", "1")
BELL_LABELS = ("00", "01", "10", "11")
console = Console(markup=False, highlight=False)

# Amplitudes follow the order of the corresponding basis labels.
State = tuple[complex, ...]
Matrix = tuple[tuple[complex, complex], tuple[complex, complex]]
Gate = tuple[str, Matrix, str]  # Menu description, matrix, explanation.
Preset = tuple[str, State, str]  # Input name, amplitudes, output description.

GATES: dict[str, Gate] = {
    "H": (
        "Hadamard",
        ((1 / SQRT_2, 1 / SQRT_2), (1 / SQRT_2, -1 / SQRT_2)),
        "New amplitudes: ((a + b)/sqrt(2), (a - b)/sqrt(2)).\n"  # This won't cause an error, python joins two adjacent string literals automatically.
        "Applying H twice restores the input: H * H = I.",
    ),
    "X": ("Bit flip", ((0, 1), (1, 0)), "X exchanges the two amplitudes."),
    "Y": (
        "Pauli Y",
        ((0, -1j), (1j, 0)),
        "Y exchanges the amplitudes and multiplies them by -j and j.",
    ),
    "Z": (
        "Phase flip",
        ((1, 0), (0, -1)),
        "Z changes phase; measurement probabilities stay the same.",
    ),
    "S": (
        "Phase pi/2",
        ((1, 0), (0, 1j)),
        "S changes phase; measurement probabilities stay the same.",
    ),
    "T": (
        "Phase pi/4",
        ((1, 0), (0, (1 + 1j) / SQRT_2)),
        "T changes phase; measurement probabilities stay the same.",
    ),
}

SINGLE_STATES: dict[str, Preset] = {
    "1": ("|0>", (1, 0), ""),
    "2": ("|1>", (0, 1), ""),
    "3": ("|+>", (1 / SQRT_2, 1 / SQRT_2), ""),
    "4": ("|->", (1 / SQRT_2, -1 / SQRT_2), ""),
}
BELL_STATES: dict[str, Preset] = {
    "1": ("|00>", (1, 0, 0, 0), "Phi+ = (|00> + |11>)/sqrt(2)"),
    "2": ("|01>", (0, 1, 0, 0), "Psi+ = (|01> + |10>)/sqrt(2)"),
    "3": ("|10>", (0, 0, 1, 0), "Phi- = (|00> - |11>)/sqrt(2)"),
    "4": ("|11>", (0, 0, 0, 1), "Psi- = (|01> - |10>)/sqrt(2)"),
}


# END AVIYANSH #


# START ALICIA #
def apply_gate(
    state: State, gate: str, inverse: bool = False
) -> tuple[complex, complex]:
    """Multiply two amplitudes by a gate matrix, or its conjugate transpose."""
    _, matrix, _ = GATES[gate]
    (p, q), (r, s) = matrix
    if inverse:
        p, q, r, s = p.conjugate(), r.conjugate(), q.conjugate(), s.conjugate()
    a, b = state
    return p * a + q * b, r * a + s * b


def format_amplitude(value: complex) -> str:
    """Round for display only; keep the original amplitudes for calculations."""
    real = 0.0 if abs(value.real) < 0.00005 else value.real
    imag = 0.0 if abs(value.imag) < 0.00005 else value.imag
    return f"{real:.4f}" if imag == 0 else f"({real:.4f}{imag:+.4f}j)"


def format_state(state: State, labels: tuple[str, ...]) -> str:
    """Attach each amplitude to its basis label, keeping real minus signs readable."""
    terms = []
    for amplitude, label in zip(state, labels, strict=True):
        if terms and amplitude.imag == 0 and amplitude.real < 0:
            terms.append(f" - {format_amplitude(-amplitude)}|{label}>")
        else:
            sign = " + " if terms else ""
            terms.append(f"{sign}{format_amplitude(amplitude)}|{label}>")
    return "".join(terms)


def normalize(state: State) -> State:
    """Rescale finite, nonzero amplitudes without squaring huge or tiny inputs."""
    if len(state) not in (2, 4):
        raise ValueError("A state must contain two or four amplitudes.")
    components = [
        part for amplitude in state for part in (amplitude.real, amplitude.imag)
    ]
    if not all(math.isfinite(part) for part in components):
        raise ValueError("Amplitudes must be finite numbers.")
    scale = max(abs(part) for part in components)
    if scale == 0:
        raise ValueError("Amplitudes cannot all be zero.")

    # Scale real and imaginary parts separately, including extremely small inputs.
    scaled = tuple(complex(a.real / scale, a.imag / scale) for a in state)
    norm = math.hypot(*(abs(a) for a in scaled))
    return tuple(a / norm for a in scaled)


def apply_bell_circuit(state: State) -> tuple[State, State]:
    """Apply H on the first qubit, then CNOT with that qubit as control."""
    a, b, c, d = state
    a, c = apply_gate((a, c), "H")
    b, d = apply_gate((b, d), "H")
    after_h = (a, b, c, d)
    # CNOT exchanges the amplitudes belonging to |10> and |11>.
    return after_h, (a, b, d, c)


# END ALICIA #


# START HITANSHI #
def read_choice(prompt: str, options: dict[str, str]) -> str:
    """Create a menu from its data and retry choices that are not listed."""
    menu = Table(box=box.SIMPLE_HEAD, header_style="bold cyan")
    menu.add_column("Key", style="cyan")
    menu.add_column(prompt)
    for key, description in options.items():
        menu.add_row(key, description)
    menu.add_row("Q", "Quit")
    console.print(menu)

    while True:
        choice = input(f"{prompt} [Q to quit]: ").strip().upper()
        if choice in options or choice == "Q":
            return choice
        console.print("Please choose one of the listed options.", style="yellow")


def read_custom_state(labels: tuple[str, ...]) -> State:
    """Read one amplitude per basis label and retry an invalid state."""
    console.print("Enter real or complex numbers, such as 0.6, -0.8, or 0.5+0.5j.")
    console.print("Here j*j = -1. Amplitudes will be normalized.", style="dim")
    while True:
        try:
            amplitudes = tuple(
                complex(input(f"  Amplitude for |{label}>: ").strip())
                for label in labels
            )
            state = normalize(amplitudes)
        except ValueError as error:
            console.print(f"  {error}", style="yellow")
            console.print("Enter finite numbers, not expressions, and try again.")
            continue
        console.print(f"Normalized input: {format_state(state, labels)}", style="green")
        return state


def read_state(presets: dict[str, Preset], labels: tuple[str, ...]) -> Preset | None:
    """Select a preset or delegate custom input; None means the user chose Quit."""
    options = {
        key: f"{name} -> {note}" if note else name
        for key, (name, _, note) in presets.items()
    }
    choice = read_choice("Starting state", {**options, "5": "Custom amplitudes"})
    if choice == "Q":
        return None
    if choice == "5":
        return "|psi>", read_custom_state(labels), ""
    return presets[choice]


# END HITANSHI #


# START VEDIKA #
def measure(state: State, shots: int) -> tuple[int, int]:
    """Sample fresh copies of an already normalized single-qubit state."""
    if shots < 1:
        raise ValueError("The number of shots must be positive.")
    a, _ = state
    probability_zero = min(1.0, max(0.0, abs(a) ** 2))
    zeros = sum(random.random() < probability_zero for _ in range(shots))
    return zeros, shots - zeros


def read_shots() -> int:
    """Read a whole number from 1 to 100000; Enter uses 1000."""
    while True:
        answer = input("Measurement shots [1000] (1-100000): ").strip()
        try:
            shots = int(answer) if answer else 1000
        except ValueError:
            console.print("Please enter a whole number.", style="yellow")
            continue
        if 1 <= shots <= 100000:
            return shots
        console.print("Please enter a number from 1 to 100000.", style="yellow")


def show_single_result(
    initial: State, result: State, gate: str, counts: tuple[int, int]
) -> None:
    """Show the calculation and compare theoretical probabilities with samples."""
    description, matrix, explanation = GATES[gate]
    matrix_text = "\n".join(
        "  ".join(format_amplitude(value) for value in row) for row in matrix
    )
    restored = apply_gate(result, gate, inverse=True)
    console.print(
        Panel(
            f"Matrix:\n{matrix_text}\n\n{explanation}\n\n"
            f"Output: {format_state(result, SINGLE_LABELS)}\n"
            f"Apply inverse (before measuring): {format_state(restored, SINGLE_LABELS)}",
            title=f"{description} [ {gate} ]",
            border_style="cyan",
        )
    )
    shots = sum(counts)
    console.print(f"Simulated measurements ({shots:,} shots)", style="bold green")
    table = Table(box=box.SIMPLE_HEAD, header_style="bold cyan")
    for heading in ("Outcome", f"Before {gate}", f"After {gate}", "Count", "Observed"):
        table.add_column(heading, justify="left" if heading == "Outcome" else "right")
    for bit, count in enumerate(counts):
        table.add_row(
            f"|{bit}>",
            f"{min(1.0, abs(initial[bit]) ** 2):.2%}",
            f"{min(1.0, abs(result[bit]) ** 2):.2%}",
            f"{count:,}",
            f"{count / shots:.2%}",
        )
    console.print(table)
    console.print(
        "Random samples may differ from the theoretical probabilities.", style="dim"
    )


# END VEDIKA #


# START SREERAM #
def show_bell_result(after_h: State, result: State, bell_name: str) -> None:
    """Show both circuit steps and check whether the pure output is entangled."""
    console.print(f"After H on first qubit: {format_state(after_h, BELL_LABELS)}")
    console.print(
        f"After CNOT: {format_state(result, BELL_LABELS)}", style="bold green"
    )
    console.print(
        f"Bell state: {bell_name}"
        if bell_name
        else "Custom output need not be a Bell state."
    )
    a, b, c, d = result
    # For a pure two-qubit state, a*d = b*c means it is separable.
    entangled = abs(a * d - b * c) > 1e-9
    console.print(f"Entangled: {'yes' if entangled else 'no'}")


def run() -> None:
    """Connect menu selection, state preparation, calculation, and output."""
    console.print(
        Panel(
            "QUANTUM GATE SIMULATOR\n\n"
            "Amplitudes describe a pure quantum state.\n"
            "Their squared magnitudes give measurement probabilities.",
            border_style="cyan",
        )
    )
    options = {key: description for key, (description, _, _) in GATES.items()}
    options["B"] = "Bell circuit: H on first qubit, then CNOT"
    while True:
        gate = read_choice("Gate or circuit", options)
        if gate == "Q":
            return
        is_bell = gate == "B"
        labels = BELL_LABELS if is_bell else SINGLE_LABELS
        presets = BELL_STATES if is_bell else SINGLE_STATES
        selected = read_state(presets, labels)
        if selected is None:
            return
        name, initial, note = selected
        console.print(f"\nInput {name}: {format_state(initial, labels)}")

        if is_bell:
            console.print(
                "q0: --H--o--\nq1: -----X--\nFirst qubit = control; second = target."
            )
            after_h, result = apply_bell_circuit(initial)
            show_bell_result(after_h, result, note)
        else:
            result = apply_gate(initial, gate)
            console.print(
                f"Each shot prepares the input again, applies {gate}, then measures.",
                style="dim",
            )
            counts = measure(result, read_shots())
            show_single_result(initial, result, gate, counts)
        console.rule(characters="-", style="dim")


def main() -> None:
    """Start the simulator and finish cleanly when the user quits or input stops."""
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        pass
    console.print("\nSimulation finished. Goodbye!", style="cyan")


if __name__ == "__main__":
    main()
# END SREERAM #
