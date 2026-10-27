"""Проверки заданий лабораторной №4 без сторонних зависимостей."""

import unittest
from math import factorial as reference_factorial

from lab4 import factorial, filter_even, log_calls, memoize, repeat


class FilterEvenTests(unittest.TestCase):
    def test_keeps_order_duplicates_zero_and_negative_numbers(self):
        numbers = [3, -4, 0, 2, -1, 2, 7]
        self.assertEqual(filter_even(numbers), [-4, 0, 2, 2])
        self.assertEqual(numbers, [3, -4, 0, 2, -1, 2, 7])

    def test_accepts_generator(self):
        self.assertEqual(filter_even(n for n in range(6)), [0, 2, 4])

    def test_empty_and_all_odd(self):
        self.assertEqual(filter_even([]), [])
        self.assertEqual(filter_even([1, 3, -5]), [])


class FactorialTests(unittest.TestCase):
    def test_matches_standard_library_including_zero(self):
        for number in (0, 1, 2, 5, 10, 50):
            with self.subTest(number=number):
                self.assertEqual(factorial(number), reference_factorial(number))

    def test_rejects_negative_number(self):
        with self.assertRaises(ValueError):
            factorial(-1)

    def test_rejects_non_integer_arguments(self):
        for value in (2.5, "5", None, True):
            with self.subTest(value=value), self.assertRaises(TypeError):
                factorial(value)


class LogCallsTests(unittest.TestCase):
    def test_logs_arguments_and_preserves_result_and_metadata(self):
        @log_calls
        def add(left, right):
            """Сложение."""
            return left + right

        with self.assertLogs("lab4", level="INFO") as captured:
            self.assertEqual(add(2, right=3), 5)
        self.assertEqual(len(captured.records), 1)
        self.assertIn("add", captured.output[0])
        self.assertIn("args=(2,)", captured.output[0])
        self.assertIn("'right': 3", captured.output[0])
        self.assertEqual(add.__name__, "add")
        self.assertEqual(add.__doc__, "Сложение.")

    def test_logs_failed_call_and_propagates_exception(self):
        @log_calls
        def fail():
            raise ValueError("ошибка")

        with self.assertLogs("lab4", level="INFO") as captured:
            with self.assertRaisesRegex(ValueError, "ошибка"):
                fail()
        self.assertEqual(len(captured.records), 1)


class MemoizeTests(unittest.TestCase):
    def test_reuses_results_and_normalizes_keyword_order(self):
        calls = []

        @memoize
        def add(left, right=0):
            """Сложение с кэшем."""
            calls.append((left, right))
            return left + right

        self.assertEqual(add(left=2, right=3), 5)
        self.assertEqual(add(right=3, left=2), 5)
        self.assertEqual(add(left=4, right=3), 7)
        self.assertEqual(calls, [(2, 3), (4, 3)])
        self.assertEqual(add.__name__, "add")
        self.assertEqual(add.__doc__, "Сложение с кэшем.")

    def test_caches_falsy_results(self):
        for result in (None, 0, False, ""):
            with self.subTest(result=result):
                calls = []

                @memoize
                def calculate(number):
                    calls.append(number)
                    return result

                self.assertEqual(calculate(1), result)
                self.assertEqual(calculate(1), result)
                self.assertEqual(calls, [1])

    def test_supports_recursive_function(self):
        calls = []

        @memoize
        def fibonacci(number):
            calls.append(number)
            return number if number < 2 else fibonacci(number - 1) + fibonacci(number - 2)

        self.assertEqual(fibonacci(10), 55)
        self.assertEqual(len(calls), 11)
        self.assertEqual(fibonacci(10), 55)
        self.assertEqual(len(calls), 11)

    def test_does_not_cache_exceptions(self):
        calls = []

        @memoize
        def fail(number):
            calls.append(number)
            raise ValueError("ошибка")

        for _ in range(2):
            with self.assertRaises(ValueError):
                fail(1)
        self.assertEqual(calls, [1, 1])

    def test_rejects_unhashable_arguments(self):
        @memoize
        def identity(value):
            return value

        with self.assertRaises(TypeError):
            identity([])

    def test_caches_are_independent(self):
        first = memoize(lambda number: number + 1)
        second = memoize(lambda number: number + 2)
        self.assertEqual(first(1), 2)
        self.assertEqual(second(1), 3)


class RepeatTests(unittest.TestCase):
    def test_repeats_with_arguments_and_returns_last_result(self):
        calls = []

        @repeat(times=3)
        def record(value, *, suffix):
            """Записать вызов."""
            calls.append(value + suffix)
            return len(calls)

        self.assertEqual(record("a", suffix="b"), 3)
        self.assertEqual(calls, ["ab", "ab", "ab"])
        self.assertEqual(record.__name__, "record")
        self.assertEqual(record.__doc__, "Записать вызов.")

    def test_one_repetition_and_none_result(self):
        calls = []

        @repeat(1)
        def record():
            calls.append(1)

        self.assertIsNone(record())
        self.assertEqual(calls, [1])

    def test_rejects_non_positive_count(self):
        for count in (0, -1):
            with self.subTest(count=count), self.assertRaises(ValueError):
                repeat(count)

    def test_rejects_non_integer_count(self):
        for count in (1.5, "3", None, True):
            with self.subTest(count=count), self.assertRaises(TypeError):
                repeat(count)

    def test_stops_on_exception(self):
        calls = []

        @repeat(3)
        def fail():
            calls.append(1)
            raise RuntimeError("ошибка")

        with self.assertRaisesRegex(RuntimeError, "ошибка"):
            fail()
        self.assertEqual(calls, [1])


if __name__ == "__main__":
    unittest.main()
