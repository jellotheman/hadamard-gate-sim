# Quantum Gate Simulator

A Python terminal program for exploring the H, X, Y, Z, S, and T single-qubit gates and
a two-qubit Bell circuit. All application code lives in `main.py`, using functions and
shared data definitions. Requires Python 3.10 or newer and Rich for terminal output.

## Set up and run

Open a terminal in the project folder and run:

```powershell
python -m pip install -r requirements.txt
python main.py
```

The first command installs Rich; it only needs to run once per Python environment. After
that, start the simulator with `python main.py`.

On Windows, use `py` instead of `python` if necessary. If you see
`No module named 'rich'`, install the requirements with the same Python command you use
to start the program. If Python cannot find `main.py`, check your current folder.

The simulator runs locally without a quantum computer or online account. Rich formats
the menus, calculation panels, and result tables; color is disabled for redirected
output.

## Your first simulation

1. Run `python main.py`. At **Gate or circuit**, enter `H` for Hadamard.
2. At **Starting state**, enter `1` for `|0>`, the state that always measures as zero.
3. At **Measurement shots**, press Enter for 1,000 trials, or enter a whole number from
   1 to 100,000. Each shot prepares the input again, applies the gate, and measures.
4. Read the gate matrix, output amplitudes, and inverse check. The result table shows
   theoretical probabilities **Before H** and **After H**, the sampled **Count**, and
   the **Observed** percentage. For this input, both after-H probabilities are 50%.
5. The gate menu returns. Try `H`, then starting state `3` (`|+>`): zero is now certain.
6. Enter `Q` at either menu to quit. Ctrl+C or end-of-input also exits cleanly.

Random counts vary between runs. With equal probabilities, 493 zeros and 507 ones is one
possible result from 1,000 shots. More shots generally give a closer approximation to
the theoretical distribution, but do not guarantee a closer result on every run.

## Gates and state representation

| Menu key | Operation                                                              |
| -------- | ---------------------------------------------------------------------- |
| `H`      | Hadamard: combines amplitudes by addition and subtraction              |
| `X`      | Bit flip: exchanges the zero and one amplitudes                        |
| `Y`      | Pauli Y: exchanges amplitudes and multiplies them by imaginary factors |
| `Z`      | Phase flip: negates the one amplitude                                  |
| `S`      | Phase gate: multiplies the one amplitude by `j`                        |
| `T`      | Phase gate: multiplies the one amplitude by `(1 + j)/sqrt(2)`          |
| `B`      | Bell circuit: H on the first qubit, followed by CNOT                   |

A single-qubit pure state is written `a|0> + b|1>` and stored as the tuple `(a, b)`. The
amplitudes may be complex. Their squared magnitudes give measurement probabilities:
`P(0) = |a|^2` and `P(1) = |b|^2`, which total one for a normalized state. For an
amplitude `x + yj`, the squared magnitude is `x*x + y*y`.

Every single-qubit gate uses the same matrix calculation:

```text
[ p  q ] [ a ] = [ p*a + q*b ]
[ r  s ] [ b ]   [ r*a + s*b ]
```

For H, this becomes:

```text
H = 1/sqrt(2) * [ 1   1 ]
                [ 1  -1 ]

H(a, b) = ((a + b)/sqrt(2), (a - b)/sqrt(2))
```

| Starting state key | Input | Output after H | P(0) | P(1) |
| ------------------ | ----- | -------------- | ---- | ---- |
| `1`                | Zero  | Plus           | 50%  | 50%  |
| `2`                | One   | Minus          | 50%  | 50%  |
| `3`                | Plus  | Zero           | 100% | 0%   |
| `4`                | Minus | One            | 0%   | 100% |

Here `|+> = (|0> + |1>)/sqrt(2)` and `|-> = (|0> - |1>)/sqrt(2)`. Their measurement
probabilities are identical, but the relative minus sign changes how amplitudes
reinforce or cancel when another gate is applied. This is interference.

Applying H twice restores the input. The simulator demonstrates reversal for every
single-qubit gate using its inverse matrix, the conjugate transpose. This calculation
acts on the unmeasured output state. Sampling uses fresh copies of that state; it does
not repeatedly measure one collapsed qubit. Z, S, and T affect phase while preserving
the computational-basis measurement probabilities.

## Custom input

Choose `5` at the starting-state menu. Enter two amplitudes for a single-qubit gate, or
four for the Bell circuit. Use finite real or complex numeric values such as `0.6`,
`-0.8`, or `0.5+0.5j`. Python uses `j` for the imaginary unit, with `j*j = -1`.
Expressions such as `1/sqrt(2)` are not accepted; enter their numeric values instead.

The simulator normalizes the amplitudes so their squared magnitudes total one. It
rescales components before calculating their norm to support very large and very small
inputs. All-zero inputs, infinities, undefined values, and invalid numeric text cause a
retry. Amplitudes are rounded to four decimal places for display only.

Examples to try with H:

- `3`, `4`: normalized to `(0.6, 0.8)`, giving output probabilities of 98% and 2%.
- `1`, `-1`: normalized to the minus state, giving one with certainty after H.
- `1`, `1j`: gives 50/50 probabilities before and after H, with different amplitudes.

## Bell circuit

Choose `B` at the gate menu. The circuit applies H to the first qubit, then CNOT with
the first qubit as control and the second as target:

```text
q0: --H--o--
q1: -----X--
```

Two-qubit states use four amplitudes, ordered as `00, 01, 10, 11`. H combines the
amplitude pairs `00, 10` and `01, 11`. CNOT then exchanges the `10` and `11` amplitudes.
The four preset inputs produce:

| Starting state key | Input   | Bell state                       |
| ------------------ | ------- | -------------------------------- |
| `1`                | `\|00>` | `Phi+ = (\|00> + \|11>)/sqrt(2)` |
| `2`                | `\|01>` | `Psi+ = (\|01> + \|10>)/sqrt(2)` |
| `3`                | `\|10>` | `Phi- = (\|00> - \|11>)/sqrt(2)` |
| `4`                | `\|11>` | `Psi- = (\|01> - \|10>)/sqrt(2)` |

The output shows the input, the intermediate state after H, the final state after CNOT,
and whether it is entangled. For a pure state `(a, b, c, d)`, separability means
`a*d = b*c`; the program reports entanglement when `abs(a*d - b*c) > 1e-9`, using a
small tolerance for floating-point rounding. Custom input need not produce a Bell state
or an entangled output. This circuit does not request measurement shots. The simulator
models pure states; mixed states are outside its scope.

## Reading the code

`main.py` contains 14 function definitions. Start with `run()` to follow how they work
together. The shared state labels let input and formatting work for both state sizes.
Gate descriptions, matrices, and explanations are stored together in `GATES`.

| Function                                            | Purpose                                                              |
| --------------------------------------------------- | -------------------------------------------------------------------- |
| `apply_gate(state, gate, inverse=False)`            | Apply a single-qubit gate or its inverse.                            |
| `format_amplitude(value)`                           | Format one real or complex amplitude.                                |
| `format_state(state, labels)`                       | Attach amplitudes to their basis labels with readable signs.         |
| `normalize(state)`                                  | Validate and normalize two or four amplitudes.                       |
| `apply_bell_circuit(state)`                         | Return the intermediate and final states of the H-then-CNOT circuit. |
| `read_choice(prompt, options)`                      | Build a menu and validate the selected key.                          |
| `read_custom_state(labels)`                         | Collect and normalize custom amplitudes, retrying invalid input.     |
| `read_state(presets, labels)`                       | Select a preset, delegate custom input, or return `None` for Quit.   |
| `measure(state, shots)`                             | Return sampled counts for zero and one.                              |
| `read_shots()`                                      | Read a valid shot count or use the default.                          |
| `show_single_result(initial, result, gate, counts)` | Display the gate calculation, reversal, and probability/count table. |
| `show_bell_result(after_h, result, bell_name)`      | Display both circuit steps and the entanglement check.               |
| `run()`                                             | Coordinate the menus and simulation paths.                           |
| `main()`                                            | Start the program and handle interrupted input cleanly.              |

Type aliases describe the data: `State` is a tuple of amplitudes, `Matrix` is a 2-by-2
gate matrix, `Gate` holds a description/matrix/explanation, and `Preset` holds an input
name/amplitudes/output description. Type annotations document these shapes; they do not
perform runtime validation. Direct callers of `apply_gate()` and `measure()` should
supply two amplitudes, and `apply_bell_circuit()` expects four. Prepare normalized
states before interpreting results as physical probabilities or sampling them.

The people markers retain the current contiguous assignments:

| Person    | Assigned section                                                  | Functions |
| --------- | ----------------------------------------------------------------- | --------: |
| Aviyansh  | Imports, types, gate definitions, and state presets               |         0 |
| Alicia    | Gate application, formatting, normalization, and Bell calculation |         5 |
| Hitanshi  | Menu creation, custom input, and state selection                  |         3 |
| Vedika    | Measurement, shot input, and single-qubit results                 |         3 |
| Sreeram   | Bell results, simulation coordination, and startup                |         3 |
| **Total** |                                                                   |    **14** |

The `if __name__ == "__main__":` block starts the interactive program when executed
directly. Importing `main` from the tests does not start the menus.

## Tests and formatting

Run the 15 automated tests in `tests/test_main.py`:

```powershell
python -m unittest discover -s tests -v
```

They cover all six single-qubit gates, inverse restoration, interference, the four Bell
presets and intermediate states, complex inputs, normalization at extreme scales,
measurement sampling, formatting, input retries, clean exits, and Windows terminal
encoding. Tests use Python's built-in `unittest` library. VS Code's Test Explorer is
configured to discover the `tests/` folder.

Install the development requirements to use the configured Black version:

```powershell
python -m pip install -r requirements-dev.txt
python -m black --check .
npx --yes prettier@3.7.4 --check .
```

To apply formatting, use `python -m black .` and `npx --yes prettier@3.7.4 --write .`.
Project settings select Black for Python and Prettier for other supported files, with
formatting on save and paste. Black's settings are in `pyproject.toml`; Prettier's
settings are in `.prettierrc.json`. The ignored local `cnot/` reference folder is
outside the application and test suite.
