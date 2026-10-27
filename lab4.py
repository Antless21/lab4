"""Лабораторная №4, вариант 2: функциональное программирование."""

import logging
from functools import reduce, wraps
from typing import Callable, Iterable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")
logger = logging.getLogger(__name__)


def filter_even(numbers: Iterable[int]) -> list[int]:
    """Вернуть чётные числа, сохранив их порядок и повторения."""
    return list(filter(lambda number: number % 2 == 0, numbers))


def factorial(number: int) -> int:
    """Вычислить факториал неотрицательного целого числа через reduce."""
    if isinstance(number, bool) or not isinstance(number, int):
        raise TypeError("Аргумент должен быть целым числом")
    if number < 0:
        raise ValueError("Факториал определён для неотрицательных чисел")
    return reduce(lambda result, item: result * item, range(1, number + 1), 1)


def log_calls(function: Callable[P, R]) -> Callable[P, R]:
    """Записать имя и аргументы каждого вызова в журнал уровня INFO."""
    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info("Вызов %s: args=%r, kwargs=%r", function.__name__, args, kwargs)
        return function(*args, **kwargs)

    return wrapper


def memoize(function: Callable[P, R]) -> Callable[P, R]:
    """Кэшировать успешные вызовы функции с хешируемыми аргументами.

    Порядок именованных аргументов не влияет на ключ. Позиционная и
    именованная формы передачи одного аргумента создают разные ключи.
    Кэш хранится в памяти отдельно для каждой декорированной функции.
    """
    cache: dict[tuple, R] = {}

    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = function(*args, **kwargs)
        return cache[key]

    return wrapper


def repeat(times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Создать декоратор: выполнить функцию times раз, вернуть последний ответ.

    При исключении выполнение прекращается, исключение передаётся вызывающему.
    """
    if isinstance(times, bool) or not isinstance(times, int):
        raise TypeError("Количество повторений должно быть целым числом")
    if times < 1:
        raise ValueError("Количество повторений должно быть положительным")

    def decorator(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            result = function(*args, **kwargs)
            for _ in range(times - 1):
                result = function(*args, **kwargs)
            return result

        return wrapper

    return decorator


def main() -> None:
    """Показать результаты всех пяти заданий."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    print("Среднее №2. Чётные числа:", filter_even(range(-3, 8)))
    print("Среднее №4. Факториал 5:", factorial(5))

    @log_calls
    def add(left: int, right: int) -> int:
        return left + right

    print("Среднее №7. Сумма с логированием:", add(3, right=4))

    calculations = 0

    @memoize
    def square(number: int) -> int:
        nonlocal calculations
        calculations += 1
        return number * number

    print("Повышенное №2. Два вызова square(6):", square(6), square(6))
    print("Фактических вычислений:", calculations)

    @repeat(times=3)
    def greet(name: str) -> str:
        message = f"Привет, {name}!"
        print(message)
        return message

    print("Повышенное №6. Декоратор с параметром times=3:")
    greet("мир")


if __name__ == "__main__":
    main()
