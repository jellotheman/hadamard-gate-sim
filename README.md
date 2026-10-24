# Hadamard Quantum Gate Simulator

A small Python CLI project that simulates the Hadamard gate on one qubit.
Requires Python 3.10 or newer and Rich for terminal formatting.

## Run

```powershell
python -m pip install -r requirements.txt
python main.py
```

Rich provides colored section headings, framed calculations, probability bars,
and tables comparing expected and observed measurement results. Color is
automatically disabled when output is redirected to a file.

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

This models pure states of one qubit; mixed states and multi-qubit circuits
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

## Check

```powershell
python -m unittest -v
```

Tests cover all four gate transformations, normalization, applying H twice,
complex amplitudes, measurement probabilities, input validation, and clean CLI exit.
