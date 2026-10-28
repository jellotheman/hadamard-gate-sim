# Hadamard Quantum Gate Simulator

A small Python CLI project that simulates the Hadamard gate on one qubit.
Requires Python 3.10 or newer and Rich for terminal formatting.

## Set up and run

Install Python 3.10 or newer if you do not already have it. Open a terminal
(PowerShell on Windows) in this project's folder: it should contain `main.py`
and `requirements.txt`. Run these commands one at a time:

```powershell
python -m pip install -r requirements.txt
python main.py
```

The first command installs Rich, the library used to format the terminal output.
The second starts the simulator. You only need to install the dependency once
per Python environment; after that, use `python main.py` to run it again.
`requirements.txt` lists the dependency and its supported version range.

If `python` is not recognized on Windows, try `py` in its place in both commands.
If you see `No module named 'rich'`, run the install command using the same
`python` (or `py`) command you use to start the program. If Python cannot find
`main.py`, check that your terminal is in the project folder.

Rich provides colored section headings, framed calculations, probability bars,
and tables comparing expected and observed measurement results. Color is
automatically disabled when output is redirected to a file.

## Your first simulation

1. Run `python main.py` and type `1`, then press Enter to start with `|0>`.
   The notation `|0>` means the qubit state that always gives zero when measured.
2. Read the gate calculation and probability table. After H, both outcomes
   have a theoretical probability of 50%.
3. At the measurement prompt, press Enter to use 1,000 shots. A **shot** is one
   fresh simulation of preparing the input, applying the gate, and measuring it.
   You can also type a whole number from 1 to 100,000.
4. Compare **Observed** (the fraction of shots that gave each result) with
   **Expected** (the calculated probability). For example, 493 zeros and 507 ones
   is a normal result for 1,000 shots with equal probabilities. Your counts will
   vary; more shots generally bring the observed fractions closer to 50%.
5. Try option `3`, the plus state: H now gives zero with 100% probability.
   Enter `Q` at the state menu when you are finished, or press Ctrl+C to exit.

This program calculates and samples quantum probabilities on your computer;
it does not require a quantum computer or an online account.

## What is a Hadamard gate?

A quantum gate is a reversible operation on a qubit's amplitudes. The Hadamard
gate, written H, turns a definite zero or one into an equal superposition:
measuring either output gives zero or one with equal probability.

The outputs differ in their relative sign: zero becomes the plus state,
while one becomes the minus state. Quantum amplitudes behave like waves:
they can reinforce or cancel each other when another gate combines them.
That is why the sign matters even when the measurement probabilities match.

For example, start with zero and apply H twice without measuring in between.
The first H creates equal amplitudes. The second adds them for the zero output
and subtracts them for the one output. The one amplitude cancels, so the result
is definitely zero again. This is interference. Measurement happens separately
and produces one classical outcome, zero or one.

H does not always produce 50/50 probabilities: it depends on the input state.
It is commonly used to prepare superpositions in quantum algorithms.

Choose one of four example states or enter custom amplitudes, inspect the gate calculation and probability
bars, then enter a measurement count (or press Enter for 1,000 shots). The menu
returns after each simulation. Enter `Q` at the state menu to quit; Ctrl+C also
exits cleanly.

## How it works

For a normalized input `a|0> + b|1>`, the Hadamard gate produces:

```text
H = 1/sqrt(2) * [ 1   1 ]
                [ 1  -1 ]

H(a, b) = ((a + b)/sqrt(2), (a - b)/sqrt(2))
```

The probability of measuring each basis state is the squared magnitude of its
amplitude (the Born rule): `P(0) = |a|^2`, `P(1) = |b|^2`.
For a complex amplitude `x + yj`, its squared magnitude is `x*x + y*y`.
The CLI shows probabilities before and after H, then applies H a second time
to demonstrate that the original state is recovered before measurement.

## Custom states

Choose option `5` and enter any nonzero pair of finite real or complex
amplitudes. These describe an arbitrary pure single-qubit state. The simulator
divides both amplitudes by `sqrt(|a|^2 + |b|^2)` so the probabilities add to 1.
Zero pairs and invalid numbers are rejected. Python uses `j` for the imaginary
unit; enter numeric values, not expressions such as `1/sqrt(2)`.

Try these examples:

- `a = 3`, `b = 4`: normalized to `(0.6, 0.8)`. After H, the probabilities
  are 98% for zero and 2% for one.
- `a = 1`, `b = -1`: normalized to the minus state. After H, one is certain.
- `a = 1`, `b = 1j`: a complex state with 50/50 probabilities both before
  and after H, but different amplitudes.

The Hadamard simulator models pure states of one qubit. For two-qubit Bell
state preparation, use the separate script described below. Mixed states
are outside the scope of this project.

| Input | Output | P(0) | P(1) |
| --- | --- | --- | --- |
| Zero | Plus | 50% | 50% |
| One | Minus | 50% | 50% |
| Plus | Zero | 100% | 0% |
| Minus | One | 0% | 100% |

Here `|+> = (|0> + |1>)/sqrt(2)` and
`|-> = (|0> - |1>)/sqrt(2)`. The relative minus sign matters even though
`|+>` and `|->` have identical measurement probabilities: applying H maps them
to different basis states. Applying H twice restores the original state.

Each measurement shot independently prepares the chosen input and applies H.
Measuring the same qubit repeatedly without preparing it again would instead
leave it in the first measured basis state. Counts here are classical random
samples of the theoretical distribution, not measurements on quantum hardware.
Displayed amplitudes are rounded to four decimal places; calculations use
full floating-point precision.

## Reading the code

The original Hadamard simulator lives in `main.py`. A **function** is a named block
of code that performs a task. Start with `run()` to follow the menu and display
flow, then look at the smaller functions it calls:

| Code | Purpose |
| --- | --- |
| `State` and `STATES` | Define the two-amplitude representation and the four menu presets. |
| `normalize(state)` | Rescales custom amplitudes so their probabilities add to 1. |
| `hadamard(state)` | Calculates the two output amplitudes using the H formula. |
| `measure(state, shots)` | Uses random numbers to simulate measurement counts. |
| `read_custom_state()` and `read_shots()` | Read keyboard input and ask again if it is invalid. |
| `format_amplitude()`, `format_state()`, `probability_bar()`, and `show_probabilities()` | Turn numbers into readable terminal output. |
| `run()` and `main()` | Coordinate the simulation and handle Ctrl+C or the end of input. |

A state is stored as a **tuple**, a fixed sequence of values: `(a, b)`.
The first amplitude belongs to `|0>` and the second to `|1>`. In Python,
`state[0]` reads the first value, and `a, b = state` gives both values names.
`abs(a) ** 2` means the squared magnitude of `a`, which gives its probability.

The annotations such as `state: State` and `-> State` describe the expected
input and return types; they do not validate or convert values themselves.
When calling the math functions directly, supply exactly two amplitudes and
normalize the state before treating it as a physical qubit or measuring it.
`hadamard()` performs the gate calculation without normalizing its input.

The final `if __name__ == "__main__":` block starts the program when you run
`python main.py`. It also lets `test_main.py` import the functions without
opening the interactive menu. That file contains automated checks;
`requirements.txt` lists the external library the project needs.

## Other single-qubit gates

Run the separate X, Y, Z, S and T simulator with:

```powershell
python single_qubit_gates.py
```

Choose a gate, then a preset or custom state. The script shows the matrix,
output amplitudes, before/after probabilities, inverse operation and sampled
measurements. Enter `Q` at either menu to quit.

`single_qubit_gates.py` imports the existing state presets, custom input,
normalization (through custom input), formatting, probability display and
measurement helpers from `main.py`. One matrix calculation handles all five
gates. Z, S and T change phase without changing measurement probabilities.

## Bell state preparation

Run the two-qubit constructor from the project folder:

```powershell
python multiple_qubit_gates.py
```

It applies Hadamard to the first qubit, then CNOT with the first qubit as
control and the second as target. The four basis inputs prepare:

| Input | Bell state |
| --- | --- |
| `\|00>` | `Phi+ = (\|00> + \|11>)/sqrt(2)` |
| `\|01>` | `Psi+ = (\|01> + \|10>)/sqrt(2)` |
| `\|10>` | `Phi- = (\|00> - \|11>)/sqrt(2)` |
| `\|11>` | `Psi- = (\|01> - \|10>)/sqrt(2)` |

Choose `5` to enter four finite real or complex amplitudes, ordered as
`00, 01, 10, 11`. The local input helper calls the shared `normalize()` function.
The display shows the input, the intermediate state after H, the final state after CNOT, and
whether the output is entangled. A custom input need not produce a Bell state.
There are no measurement shots or probability tables in this script.

The script reuses `hadamard()`, `normalize()`, `format_amplitude()` and the
console from `main.py`, plus `read_choice()` from `single_qubit_gates.py`.
Only `normalize()` in `main.py` was extended to handle four amplitudes.
The original single-qubit `format_state()` and `read_custom_state()` are
preserved; `multiple_qubit_gates.py` has its own simple four-amplitude
versions. The initial `cnot/` implementation is not imported or used.

For the presentation, explain the new file in these chunks:

1. **Display:** `format_state()` attaches each amplitude to its basis label.
   It writes the first term, then appends the other three using plus or minus.
   The imported `format_amplitude()` still handles the number formatting.
2. **Custom input:** `read_custom_state()` collects four complex numbers in a
   loop, calls the imported `normalize()`, and retries invalid input.
3. **Gate calculations:** `hadamard_first()` calls the existing `hadamard()`
   on the pairs `00, 10` and `01, 11`. Each pair differs only in the first
   qubit. `cnot()` then exchanges the `10` and `11` amplitudes.
4. **Simulation:** `run()` gets the user's choice through the imported
   `read_choice()`, applies H followed by CNOT, and prints each step.
   For amplitudes `(a, b, c, d)`, a pure state is entangled when `a*d - b*c`
   is nonzero. The code uses a small tolerance for floating-point rounding.
5. **Startup:** `main()` runs the menu and handles Ctrl+C or end-of-input.

## Function counts and presentation split

Count definitions in the three application files only. Imported functions
are counted where they are defined, not again in each importing file.
Tests and the unused initial `cnot/` implementation are excluded.

| File | Function definitions |
| --- | ---: |
| `main.py` | 11 |
| `single_qubit_gates.py` | 4 |
| `multiple_qubit_gates.py` | 6 |
| Total with `main.py` | 21 |
| Total without `main.py` | 10 |

Keep the existing five-person allocation of `main.py`. For the other two
files, the following logical split gives two people the main technical work
and each remaining person two functions:

| Presenter | Functions | Count | Topic |
| --- | --- | ---: | --- |
| 1 | `single_qubit_gates.apply_gate`, `multiple_qubit_gates.hadamard_first`, `multiple_qubit_gates.cnot` | 3 | Gate matrices, inverse, H on amplitude pairs, controlled flip |
| 2 | `multiple_qubit_gates.run` | 1 | Construct all four Bell states, connect helpers and explain the entanglement check |
| 3 | `single_qubit_gates.read_choice`, `multiple_qubit_gates.read_custom_state` | 2 | Menus, four-amplitude input and validation |
| 4 | `single_qubit_gates.run`, `single_qubit_gates.main` | 2 | Single-qubit simulation flow, startup and clean exit |
| 5 | `multiple_qubit_gates.format_state`, `multiple_qubit_gates.main` | 2 | Two-qubit state display, startup and clean exit |

The two `main()` functions and two `run()` functions are separate definitions,
even though they share names. The table assigns the 10 definitions outside
`main.py`; the 11 definitions in `main.py` retain their existing allocation.

## Run the checks

From the project folder, after installing the dependency, run:

```powershell
python -m unittest -v
```

Tests cover all four gate transformations, normalization, applying H twice,
complex amplitudes, measurement probabilities, input validation, and clean CLI exit.
They also cover X/Y/Z/S/T, all four Bell states, four-amplitude custom input,
and two-qubit gate reversal.
Each line reports a check; `OK` at the end means they all passed. These checks
use Python's built-in `unittest` library, so no extra testing package is needed.
