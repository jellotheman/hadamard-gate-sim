"""Check Bell preparation, shared four-amplitude helpers, and the CLI."""

import contextlib
import io
import unittest
from unittest.mock import patch

from main import SQRT_2, normalize
from multiple_qubit_gates import STATES, cnot, format_state, hadamard_first, main


class BellStateTests(unittest.TestCase):
    def assertStateAlmostEqual(self, actual, expected):
        self.assertEqual(len(actual), len(expected))
        for amplitude, target in zip(actual, expected):
            self.assertAlmostEqual(amplitude, target)

    def test_all_four_bell_states(self):
        s = 1 / SQRT_2
        outputs = ((s, 0, 0, s), (0, s, s, 0), (s, 0, 0, -s), (0, s, -s, 0))
        for (_, state, _), expected in zip(STATES.values(), outputs):
            with self.subTest(state=state):
                a, b, c, d = cnot(hadamard_first(state))
                self.assertStateAlmostEqual((a, b, c, d), expected)
                self.assertAlmostEqual(2 * abs(a * d - b * c), 1)

    def test_complex_input_preserves_norm_and_reverses(self):
        state = normalize((1 + 2j, -3j, 4, -2 + 1j))
        result = cnot(hadamard_first(state))
        self.assertAlmostEqual(sum(abs(a) ** 2 for a in result), 1)
        self.assertStateAlmostEqual(hadamard_first(cnot(result)), state)

    def test_cnot_truth_table(self):
        for index, target in enumerate((0, 1, 3, 2)):
            state = tuple(int(bit == index) for bit in range(4))
            expected = tuple(int(bit == target) for bit in range(4))
            self.assertEqual(cnot(state), expected)

    def test_four_amplitude_normalization(self):
        for scale in (1, 1e300, 1e-300):
            with self.subTest(scale=scale):
                self.assertStateAlmostEqual(normalize((scale, 1j * scale, -scale, -1j * scale)),
                                           (0.5, 0.5j, -0.5, -0.5j))
        for state in ((0, 0, 0, 0), (1, 0, float("nan"), 0), (0, 1, 0, complex(0, float("inf")))):
            with self.subTest(state=state), self.assertRaises(ValueError):
                normalize(state)

    def test_four_amplitude_formatting(self):
        self.assertEqual(format_state((0.5, -0.5, 0.5j, -0.5j)),
                         "0.5000|00> - 0.5000|01> + (0.0000+0.5000j)|10> + (0.0000-0.5000j)|11>")

    def test_cli_prepares_all_presets_without_measurements(self):
        with patch("builtins.input", side_effect=["bad", "1", "2", "3", "4", "q"]), \
             patch("main.read_shots") as shots, patch("main.show_probabilities") as probabilities, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            main()
        text = output.getvalue()
        for _, _, bell in STATES.values():
            self.assertIn(f"Bell state: {bell}", text)
        self.assertEqual(text.count("Entangled: yes"), 4)
        self.assertEqual(text.count("After H on first qubit:"), 4)
        self.assertIn("Please choose", text)
        shots.assert_not_called()
        probabilities.assert_not_called()

    def test_custom_input_retries_invalid_values(self):
        answers = ["5", "bad", "0", "0", "0", "0", "nan", "0", "0", "1", "1", "1j", "-1", "-1j", "q"]
        with patch("builtins.input", side_effect=answers), contextlib.redirect_stdout(io.StringIO()) as output:
            main()
        text = output.getvalue()
        self.assertIn("Enter numbers like", text)
        self.assertIn("All amplitudes cannot be zero", text)
        self.assertIn("Amplitudes must be finite", text)
        self.assertIn("Normalized input:", text)
        self.assertIn("Custom output need not be a Bell state", text)
        self.assertIn("After CNOT:", text)

    def test_custom_output_can_be_unentangled(self):
        with patch("builtins.input", side_effect=["5", "1", "0", "1", "0", "q"]), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            main()
        self.assertIn("Entangled: no", output.getvalue())

    def test_clean_exit(self):
        for answers in (["q"], [EOFError], [KeyboardInterrupt]):
            with self.subTest(answers=answers):
                with patch("builtins.input", side_effect=answers), contextlib.redirect_stdout(io.StringIO()) as output:
                    main()
                self.assertIn("Goodbye!", output.getvalue())


if __name__ == "__main__":
    unittest.main()
