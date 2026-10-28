"""Check gate mathematics, sampling, and the interactive flow."""

import contextlib
import io
import math
import unittest
from unittest.mock import patch

from rich.console import Console

from main import STATES, format_state, hadamard, main, measure, normalize


class HadamardTests(unittest.TestCase):
    def assertStateAlmostEqual(self, actual, expected):
        for amplitude, target in zip(actual, expected):
            self.assertAlmostEqual(amplitude, target)

    def test_known_gate_outputs(self):
        s = 1 / math.sqrt(2)
        expected = [(s, s), (s, -s), (1, 0), (0, 1)]
        for (_, state), output in zip(STATES.values(), expected):
            with self.subTest(state=state):
                self.assertStateAlmostEqual(hadamard(state), output)

    def test_two_gates_restore_input_and_preserve_norm(self):
        for state in [(0.6, -0.8), (-1, 0), (0, 1), (0.5 + 0.5j, 0.5 - 0.5j)]:
            with self.subTest(state=state):
                output = hadamard(state)
                self.assertAlmostEqual(sum(abs(a) ** 2 for a in output), 1)
                self.assertStateAlmostEqual(hadamard(output), state)

    def test_measurement_basis_states(self):
        self.assertEqual(measure((1, 0), 100), (100, 0))
        self.assertEqual(measure((0, 1), 100), (0, 100))

    def test_measurement_uses_born_probabilities(self):
        with patch("main.random.random", side_effect=[0.1, 0.3, 0.7, 0.9]):
            self.assertEqual(measure((0.6, 0.8), 4), (2, 2))

    def test_nonpositive_shots_rejected(self):
        with self.assertRaises(ValueError):
            measure((1, 0), 0)

    def test_normalize_custom_amplitudes(self):
        self.assertStateAlmostEqual(normalize((3, 4)), (0.6, 0.8))
        for scale in [1, 1e300, 1e-300]:
            with self.subTest(scale=scale):
                state = normalize((scale, scale * 1j))
                s = 1 / math.sqrt(2)
                self.assertStateAlmostEqual(state, (s, s * 1j))

    def test_invalid_amplitudes_rejected(self):
        for state in [(0, 0), (float("nan"), 1), (1, complex(0, float("inf")))]:
            with self.subTest(state=state):
                with self.assertRaises(ValueError):
                    normalize(state)

    def test_complex_interference_and_measurement(self):
        result = hadamard((0.5 + 0.5j, 0.5 - 0.5j))
        s = 1 / math.sqrt(2)
        self.assertStateAlmostEqual(result, (s, s * 1j))
        with patch("main.random.random", side_effect=[0.1, 0.4, 0.6, 0.9]):
            self.assertEqual(measure(result, 4), (2, 2))

    def test_complex_display_preserves_phase(self):
        self.assertEqual(
            format_state((0.5 + 0.5j, -0.5j)),
            "(0.5000+0.5000j)|0> + (0.0000-0.5000j)|1>",
        )

    def test_custom_cli_retries_invalid_amplitudes(self):
        answers = ["5", "bad", "0", "0", "nan", "1", "3", "4", "1", "q"]
        with patch("builtins.input", side_effect=answers):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                main()
        text = output.getvalue()
        self.assertIn("Both amplitudes cannot be zero", text)
        self.assertIn("Amplitudes must be finite", text)
        self.assertIn("Normalized input: 0.6000|0> + 0.8000|1>", text)
        self.assertIn("Output: 0.9899|0> - 0.1414|1>", text)

    def test_cli_reprompts_and_runs_all_states(self):
        answers = [
            "bad",
            "1",
            "abc",
            "0",
            "100001",
            "10",
            "2",
            "",
            "3",
            "1",
            "4",
            "1",
            "Q",
        ]
        output = io.StringIO()
        with patch("builtins.input", side_effect=answers):
            with contextlib.redirect_stdout(output):
                main()
        text = output.getvalue()
        self.assertEqual(text.count("[2 / PROCESSING]"), 4)
        self.assertEqual(text.count("Simulated measurements"), 4)
        self.assertIn("1,000 shots", text)
        self.assertIn("Goodbye!", text)

    def test_eof_exits_cleanly(self):
        with patch("builtins.input", side_effect=EOFError):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                main()
        self.assertIn("Goodbye!", output.getvalue())

    def test_legacy_windows_encoding(self):
        buffer = io.BytesIO()
        stream = io.TextIOWrapper(buffer, encoding="cp1252")
        terminal = Console(file=stream, width=80, color_system=None)
        with patch("main.console", terminal):
            with patch("builtins.input", side_effect=["1", "1", "q"]):
                main()
        stream.flush()
        self.assertIn(b"Goodbye!", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
