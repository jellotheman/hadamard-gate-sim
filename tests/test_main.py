"""Check the consolidated simulator's mathematics and interactive workflows."""

import io
import math
import unittest
from unittest.mock import patch

from rich.console import Console

import main as sim


class SimulatorTests(unittest.TestCase):
    def assertStateAlmostEqual(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for amplitude, target in zip(actual, expected):
            self.assertAlmostEqual(amplitude, target)

    def run_cli(self, answers):
        output = io.StringIO()
        with (
            patch.object(
                sim, "console", Console(file=output, width=120, color_system=None)
            ),
            patch("builtins.input", side_effect=answers),
        ):
            sim.main()
        return output.getvalue()

    def test_all_single_gate_basis_outputs(self):
        s = 1 / math.sqrt(2)
        expected = {
            "H": ((s, s), (s, -s)),
            "X": ((0, 1), (1, 0)),
            "Y": ((0, 1j), (-1j, 0)),
            "Z": ((1, 0), (0, -1)),
            "S": ((1, 0), (0, 1j)),
            "T": ((1, 0), (0, complex(s, s))),
        }
        for gate, outputs in expected.items():
            for state, target in zip(((1, 0), (0, 1)), outputs):
                with self.subTest(gate=gate, state=state):
                    self.assertStateAlmostEqual(sim.apply_gate(state, gate), target)

    def test_all_gates_preserve_norm_and_inverse_restores_complex_input(self):
        states = [state for _, state, _ in sim.SINGLE_STATES.values()]
        states.append(sim.normalize((1 + 2j, -3 + 4j)))
        for gate in sim.GATES:
            for state in states:
                with self.subTest(gate=gate, state=state):
                    result = sim.apply_gate(state, gate)
                    self.assertAlmostEqual(sum(abs(a) ** 2 for a in result), 1)
                    self.assertStateAlmostEqual(
                        sim.apply_gate(result, gate, inverse=True), state
                    )

    def test_hadamard_plus_and_minus_and_complex_interference(self):
        s = 1 / sim.SQRT_2
        for state, expected in (
            ((s, s), (1, 0)),
            ((s, -s), (0, 1)),
            ((0.5 + 0.5j, 0.5 - 0.5j), (s, s * 1j)),
        ):
            with self.subTest(state=state):
                self.assertStateAlmostEqual(sim.apply_gate(state, "H"), expected)

    def test_all_bell_presets_and_intermediate_states(self):
        s = 1 / sim.SQRT_2
        expected = (
            ((s, 0, s, 0), (s, 0, 0, s)),
            ((0, s, 0, s), (0, s, s, 0)),
            ((s, 0, -s, 0), (s, 0, 0, -s)),
            ((0, s, 0, -s), (0, s, -s, 0)),
        )
        for (_, state, _), (middle, final) in zip(sim.BELL_STATES.values(), expected):
            with self.subTest(state=state):
                after_h, result = sim.apply_bell_circuit(state)
                self.assertStateAlmostEqual(after_h, middle)
                self.assertStateAlmostEqual(result, final)

    def test_complex_bell_circuit_preserves_norm_and_reverses(self):
        state = sim.normalize((1 + 2j, -3j, 4, -2 + 1j))
        after_h, result = sim.apply_bell_circuit(state)
        for stage in (after_h, result):
            self.assertAlmostEqual(sum(abs(a) ** 2 for a in stage), 1)
        a, b, d, c = result  # Undo CNOT before undoing H on the first qubit.
        a, c = sim.apply_gate((a, c), "H", inverse=True)
        b, d = sim.apply_gate((b, d), "H", inverse=True)
        self.assertStateAlmostEqual((a, b, c, d), state)

    def test_normalization_handles_both_sizes_and_extreme_scales(self):
        self.assertStateAlmostEqual(sim.normalize((3, 4)), (0.6, 0.8))
        for scale in (1, 1e300, 1e-300, 5e-324):
            for phases in ((1, 1j), (1, 1j, -1, -1j)):
                with self.subTest(scale=scale, phases=phases):
                    state = tuple(
                        complex(a.real * scale, a.imag * scale) for a in phases
                    )
                    expected = tuple(a / math.sqrt(len(phases)) for a in phases)
                    self.assertStateAlmostEqual(sim.normalize(state), expected)

    def test_invalid_states_are_rejected(self):
        for state in (
            (),
            (1,),
            (1, 0, 0),
            (0, 0),
            (0, 0, 0, 0),
            (float("nan"), 1),
            (1, complex(0, float("inf"))),
        ):
            with self.subTest(state=state), self.assertRaises(ValueError):
                sim.normalize(state)

    def test_measurement_uses_squared_magnitudes_and_total_shots(self):
        self.assertEqual(sim.measure((1, 0), 4), (4, 0))
        self.assertEqual(sim.measure((0, 1), 4), (0, 4))
        with patch.object(sim.random, "random", side_effect=[0.1, 0.3, 0.7, 0.9]):
            self.assertEqual(sim.measure((0.6j, 0.8), 4), (2, 2))
        for shots in (0, -1):
            with self.subTest(shots=shots), self.assertRaises(ValueError):
                sim.measure((1, 0), shots)

    def test_shared_formatting_handles_signs_complex_values_and_label_mismatches(self):
        self.assertEqual(
            sim.format_state((-0.5, 0.5j), sim.SINGLE_LABELS),
            "-0.5000|0> + (0.0000+0.5000j)|1>",
        )
        self.assertEqual(
            sim.format_state((0.5, -0.5, 0.5j, -0.5j), sim.BELL_LABELS),
            "0.5000|00> - 0.5000|01> + (0.0000+0.5000j)|10> + (0.0000-0.5000j)|11>",
        )
        self.assertEqual(sim.format_amplitude(complex(-1e-8, 1e-8)), "0.0000")
        with self.assertRaises(ValueError):
            sim.format_state((1, 0), sim.BELL_LABELS)

    def test_cli_all_single_gates_and_invalid_choices_and_shots(self):
        answers = ["bad", "h", "bad", "1", "abc", "0", "100001", ""]
        for gate in ("X", "Y", "Z", "S", "T"):
            answers.extend((gate, "3", "1"))
        text = self.run_cli([*answers, "q"])
        for gate in sim.GATES:
            self.assertIn(f"[ {gate} ]", text)
            self.assertIn(f"Before {gate}", text)
            self.assertIn(f"After {gate}", text)
        self.assertEqual(text.count("Apply inverse"), 6)
        self.assertIn("1,000 shots", text)
        self.assertIn("Please enter a whole number", text)
        self.assertIn("Please enter a number from 1 to 100000", text)
        self.assertIn("Goodbye!", text)

    def test_cli_custom_single_state_retries_invalid_input(self):
        text = self.run_cli(["H", "5", "bad", "0", "0", "nan", "1", "3", "4", "1", "Q"])
        self.assertIn("Amplitudes cannot all be zero", text)
        self.assertIn("Amplitudes must be finite", text)
        self.assertIn("Normalized input: 0.6000|0> + 0.8000|1>", text)
        self.assertIn("Output: 0.9899|0> - 0.1414|1>", text)

    def test_cli_bell_presets_never_measure(self):
        answers = [choice for key in sim.BELL_STATES for choice in ("B", key)]
        with (
            patch.object(sim, "read_shots") as shots,
            patch.object(sim, "measure") as measure,
            patch.object(sim, "show_single_result") as single_output,
        ):
            text = self.run_cli([*answers, "Q"])
        for _, _, bell in sim.BELL_STATES.values():
            self.assertIn(f"Bell state: {bell}", text)
        self.assertEqual(text.count("After H on first qubit:"), 4)
        self.assertEqual(text.count("Entangled: yes"), 4)
        shots.assert_not_called()
        measure.assert_not_called()
        single_output.assert_not_called()

    def test_cli_bell_custom_input_can_produce_separable_output(self):
        text = self.run_cli(
            ["B", "5", "bad", "0", "0", "0", "0", "1", "0", "1", "0", "Q"]
        )
        self.assertIn("Amplitudes cannot all be zero", text)
        self.assertIn("Normalized input:", text)
        self.assertIn("Custom output need not be a Bell state", text)
        self.assertIn("Entangled: no", text)

    def test_quit_and_interruptions_at_different_prompts(self):
        for answers in (
            ["Q"],
            ["H", "Q"],
            ["B", "Q"],
            [EOFError],
            [KeyboardInterrupt],
            ["H", "5", EOFError],
            ["B", "5", KeyboardInterrupt],
            ["X", "1", EOFError],
        ):
            with self.subTest(answers=answers):
                self.assertEqual(self.run_cli(answers).count("Goodbye!"), 1)

    def test_legacy_windows_terminal_encoding(self):
        buffer = io.BytesIO()
        stream = io.TextIOWrapper(buffer, encoding="cp1252")
        with (
            patch.object(
                sim, "console", Console(file=stream, width=80, color_system=None)
            ),
            patch("builtins.input", side_effect=["Y", "2", "1", "B", "4", "Q"]),
        ):
            sim.main()
        stream.flush()
        self.assertIn(b"Goodbye!", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
