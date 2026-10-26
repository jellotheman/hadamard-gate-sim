"""Check the additional gates and their shared interactive flow."""

import contextlib
import io
import math
import unittest
from unittest.mock import patch

from main import STATES
from single_qubit_gates import GATES, apply_gate, main


class SingleQubitGateTests(unittest.TestCase):
    def assertStateAlmostEqual(self, actual, expected):
        self.assertEqual(len(actual), 2)
        for amplitude, target in zip(actual, expected):
            self.assertAlmostEqual(amplitude, target)

    def test_basis_outputs(self):
        s = 1 / math.sqrt(2)
        expected = {
            "X": ((0, 1), (1, 0)),
            "Y": ((0, 1j), (-1j, 0)),
            "Z": ((1, 0), (0, -1)),
            "S": ((1, 0), (0, 1j)),
            "T": ((1, 0), (0, complex(s, s))),
        }
        for gate, outputs in expected.items():
            for state, output in zip(((1, 0), (0, 1)), outputs):
                with self.subTest(gate=gate, state=state):
                    self.assertStateAlmostEqual(apply_gate(state, gate), output)

    def test_norm_and_inverse_for_presets_and_complex_states(self):
        states = [state for _, state in STATES.values()] + [(0.6, -0.8), (0.5+0.5j, 0.5-0.5j)]
        for gate in GATES:
            for state in states:
                with self.subTest(gate=gate, state=state):
                    result = apply_gate(state, gate)
                    self.assertAlmostEqual(sum(abs(a) ** 2 for a in result), 1)
                    self.assertStateAlmostEqual(apply_gate(result, gate, inverse=True), state)

    def test_cli_all_gates_and_custom_input(self):
        answers = ["bad", "x", "bad", "1", "4", "y", "2", "4",
                   "z", "3", "4", "s", "4", "4", "t", "5", "3", "4", "4", "q"]
        with patch("builtins.input", side_effect=answers), contextlib.redirect_stdout(io.StringIO()) as output:
            main()
        text = output.getvalue()
        for gate in GATES:
            self.assertIn(f"[ {gate} ]", text)
            self.assertIn(f"Before {gate}", text)
            self.assertIn(f"After {gate}", text)
        self.assertEqual(text.count("Apply inverse"), 5)
        self.assertIn("Normalized input: 0.6000|0> + 0.8000|1>", text)
        self.assertIn("expected 36.00%", text)
        self.assertIn("Goodbye!", text)
        self.assertNotIn("Before H", text)

    def test_quit_and_interrupted_input(self):
        for answers in (["q"], ["x", "q"], [EOFError], [KeyboardInterrupt]):
            with self.subTest(answers=answers):
                with patch("builtins.input", side_effect=answers), contextlib.redirect_stdout(io.StringIO()) as output:
                    main()
                self.assertIn("Goodbye!", output.getvalue())


if __name__ == "__main__":
    unittest.main()
