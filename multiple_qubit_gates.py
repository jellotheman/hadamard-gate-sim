"""Prepare Bell states with H on the first qubit, followed by CNOT."""

from main import console, format_amplitude, hadamard, normalize
from single_qubit_gates import read_choice

LABELS = ("00", "01", "10", "11")
State = tuple[complex, ...]  # Four amplitudes, in the same order as LABELS.
# Menu key: (input name, amplitudes, Bell state produced by H then CNOT).
STATES = {
    "1": ("|00>", (1, 0, 0, 0), "Phi+ = (|00> + |11>)/sqrt(2)"),
    "2": ("|01>", (0, 1, 0, 0), "Psi+ = (|01> + |10>)/sqrt(2)"),
    "3": ("|10>", (0, 0, 1, 0), "Phi- = (|00> - |11>)/sqrt(2)"),
    "4": ("|11>", (0, 0, 0, 1), "Psi- = (|01> - |10>)/sqrt(2)"),
}


# Two-qubit display and input
def format_state(state: State) -> str:
    # Write the first term, then add the other three with readable signs.
    text = f"{format_amplitude(state[0])}|00>"
    for amplitude, label in zip(state[1:], LABELS[1:]):
        if amplitude.imag == 0 and amplitude.real < 0:
            text += f" - {format_amplitude(-amplitude)}|{label}>"
        else:
            text += f" + {format_amplitude(amplitude)}|{label}>"
    return text


def read_custom_state() -> State:
    console.print("\nEnter four real or complex amplitudes in order: 00, 01, 10, 11.")
    console.print("Use j for the imaginary unit, for example 0.5+0.5j.", style="dim")
    while True:
        try:
            amplitudes = []
            for label in LABELS:
                amplitude = complex(input(f"  Amplitude for |{label}>: ").strip())
                amplitudes.append(amplitude)
            state = normalize(tuple(amplitudes))
        except ValueError as error:
            console.print(f"  {error}", style="yellow")
            console.print(
                "  Enter numbers like 0.6, -0.8, or 0.5+0.5j.", style="yellow"
            )
            continue
        console.print(f"  Normalized input: {format_state(state)}", style="green")
        return state


# Gate calculations
def hadamard_first(state: State) -> State:
    # Apply the existing single-qubit H to pairs differing in the first bit.
    a, b, c, d = state
    a, c = hadamard((a, c))
    b, d = hadamard((b, d))
    return a, b, c, d


def cnot(state: State) -> State:
    # First qubit controls the second: exchange the |10> and |11> amplitudes.
    a, b, c, d = state
    return a, b, d, c


# Simulation flow
def run() -> None:
    console.print("\nBELL STATE CONSTRUCTOR", style="bold cyan")
    console.print("q0: --H--o--\nq1: -----X--\nFirst qubit = control; second = target.")
    while True:
        options = {key: f"{name} -> {bell}" for key, (name, _, bell) in STATES.items()}
        choice = read_choice(
            "Starting state", {**options, "5": "Custom: four complex amplitudes"}
        )
        if choice == "Q":
            return
        if choice == "5":
            name = "|psi>"
            initial = read_custom_state()
            bell = None
        else:
            name, initial, bell = STATES[choice]
        after_h = hadamard_first(initial)
        result = cnot(after_h)
        console.print(f"\nInput {name}: {format_state(initial)}")
        console.print(f"After H on first qubit: {format_state(after_h)}")
        console.print(f"After CNOT: {format_state(result)}", style="bold green")
        console.print(
            f"Bell state: {bell}" if bell else "Custom output need not be a Bell state."
        )
        a, b, c, d = result
        # For a pure two-qubit state, a*d = b*c means the qubits are separable.
        if abs(a * d - b * c) > 1e-9:
            console.print("Entangled: yes")
        else:
            console.print("Entangled: no")


# Program entry and clean exit
def main() -> None:
    try:
        run()
    except (KeyboardInterrupt, EOFError):
        pass
    console.print("\nSimulation finished. Goodbye!", style="cyan")


if __name__ == "__main__":
    main()
