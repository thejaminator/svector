import pytest


@pytest.mark.skip("For docs only")
def test_docs_typesafety() -> None:
    from svector import Svector

    many_strings = Svector.of(["Lucy, Damion, Jon"])  # Svector[str]
    many_strings.sum()  # Mypy errors with 'Invalid self argument'. You can't sum a sequence of strings!

    many_nums = Svector.of([1, 1.2])
    assert many_nums.sum() == 2.2  # ok!

    class CannotSortMe:
        def __init__(self, value: int):
            self.value: int = value

    stuff = Svector.of([CannotSortMe(value=1), CannotSortMe(value=1)])
    stuff.sort_by(lambda x: x)  # Mypy errors with 'Cannot be "CannotSortMe"'. You can't sort by the class itself
    stuff.sort_by(lambda x: x.value)  # ok! You can sort by the value

    Svector.of([{"i am a dict": "value"}]).distinct_by(
        lambda x: x
    )  # Mypy errors with 'Cannot be Dict[str, str]. You can't hash a dict itself


@pytest.mark.skip("For docs only")
def test_fluent_methods() -> None:
    from svector import Svector

    Svector.of([-1, 0, 1]).map(lambda x: x if x >= 0 else None).flatten_option()  # Mypy infers Svector[int] correctly

    result = (
        Svector.of(i for i in range(5000))
        .map(lambda x: (x % 3, x))
        .filter(lambda x: x[0] == 0)
        .for_each_enumerate(lambda idx, element: print(f"{idx}: {element}"))
        .take(5)
    )
