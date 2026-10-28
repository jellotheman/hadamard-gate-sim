"""Simulate X, Y, Z, S and T using the original simulator's shared helpers."""

from main import (
    SQRT_2,
    STATES,
    State,
    console,
    format_state,
    measure,
    read_custom_state,
    read_shots,
    show_probabilities,
)

# Each matrix transforms the two input amplitudes into two output amplitudes.
GATES = {
    "X": ((0, 1), (1, 0)),
    "Y": ((0, -1j), (1j, 0)),
    "Z": ((1, 0), (0, -1)),
    "S": ((1, 0), (0, 1j)),
    "T": ((1, 0), (0, (1 + 1j) / SQRT_2)),
}


# Gate calculation
def apply_gate(state: State, gate: str, inverse: bool = False) -> State:
    matrix = GATES[gate]

    if inverse:
        # A quantum gate's inverse is its conjugate transpose.
        matrix = tuple(tuple(v.conjugate() for v in col) for col in zip(*matrix))

    a, b = state
    (p, q), (r, s) = matrix

    return p * a + q * b, r * a + s * b


# Shared menu input (also used by multiple_qubit_gates.py)
def read_choice(prompt: str, options: dict) -> str:
    while True:
        console.print(
            "\n" + " / ".join(f"{key}: {label}" for key, label in options.items())
        )

        choice = input(f"{prompt} [Q to quit]: ").strip().upper()

        if choice in options or choice == "Q":
            return choice

        console.print("Please choose one of the listed options.", style="yellow")


# Simulation flow
def run() -> None:
    console.print("\nSINGLE-QUBIT GATES: X, Y, Z, S, T", style="bold cyan")

    while True:
        gate = read_choice(
            "Gate",
            {
                "X": "Bit flip",
                "Y": "Pauli Y",
                "Z": "Phase flip",
                "S": "Phase pi/2",
                "T": "Phase pi/4",
            },
        )

        if gate == "Q":
            return

        choice = read_choice(
            "Starting state", {**{k: v[0] for k, v in STATES.items()}, "5": "Custom"}
        )

        if choice == "Q":
            return

        name, initial = (
            ("|psi>", read_custom_state()) if choice == "5" else STATES[choice]
        )

        result = apply_gate(initial, gate)

        console.print(f"\n{name} ----[ {gate} ]---- output", style="bold cyan")
        console.print(f"Matrix: {GATES[gate][0]}\n        {GATES[gate][1]}")
        console.print(
            f"Input:  {format_state(initial)}\nOutput: {format_state(result)}"
        )

        show_probabilities(initial, result, gate)

        console.print(
            f"Apply inverse (before measuring): {format_state(apply_gate(result, gate, inverse=True))}"
        )

        if gate in ("Z", "S", "T"):
            console.print(
                "This gate changes phase; measurement probabilities stay the same.",
                style="dim",
            )

        console.print(
            f"\nEach shot prepares the input again, applies {gate}, then measures.",
            style="dim",
        )

        shots = read_shots()

        for bit, count in enumerate(measure(result, shots)):
            console.print(
                f"|{bit}>: {count:,}/{shots:,} ({count / shots:.2%}); expected {min(1.0, abs(result[bit]) ** 2):.2%}"
            )


# Program entry and clean exit
def main() -> None:
    try:
        run()

    except (KeyboardInterrupt, EOFError):
        pass

    console.print("\nSimulation finished. Goodbye!", style="cyan")


if __name__ == "__main__":
    main()
