from dataclasses import dataclass

import pytest
from pydantic import BaseModel

from svector.immutable_tree import Svector, identity
from svector.pydantic_compat import SvectorPydantic


def test_of():
    assert Svector.of([1, 2, 3]).to_list() == [1, 2, 3]
    assert Svector.of([]).to_list() == []
    assert Svector.empty().to_list() == []
    assert Svector.of(item for item in range(1, 5)).to_list() == [1, 2, 3, 4]


def test_length():
    assert Svector.of([1, 2, 3]).length == 3
    assert Svector.of([]).length == 0


def test_map():
    assert Svector.of([1, 2, 3]).map(lambda x: x * 3) == Svector.of([3, 6, 9])
    assert Svector.of([]).map(lambda x: x * 3) == Svector.of([])


def test_flatten_iter():
    assert Svector.of([[1], [2, 2], [3, 3, 3]]).flatten_iter() == Svector.of([1, 2, 2, 3, 3, 3])
    assert Svector.of([Svector.empty(), [2, 2], [3, 3, 3]]).flatten_iter() == Svector.of([2, 2, 3, 3, 3])
    assert Svector.of([[], [2, 2], [3, 3, 3]]).flatten_iter() == Svector.of([2, 2, 3, 3, 3])  # type: ignore


def test_is_empty():
    assert Svector.of([123]).is_empty is False
    assert Svector.of([]).is_empty is True


def test_take():
    assert Svector.of([]).take(1) == Svector.of([])
    assert Svector.of([1, 2, 3]).take(0) == Svector.of([])
    assert Svector.of([1, 2, 3]).take(1) == Svector.of([1])
    assert Svector.of([1, 2, 3]).take(2) == Svector.of([1, 2])
    assert Svector.of([1, 2, 3]).take(3) == Svector.of([1, 2, 3])


def test_append():
    assert Svector.of([]).append(0) == Svector.of([0])
    assert Svector.of([]).append(1).append(2) == Svector.of([1, 2])


def test_extend():
    assert Svector.of([]).extend([1, 2, 3]) == Svector.of([1, 2, 3])
    assert Svector.of([1]).extend(["boban", "gloria"]) == Svector.of([1, "boban", "gloria"])


def test__init__():
    assert Svector([1, 2, 3]) == Svector.of([1, 2, 3])
    Svector.of([]).new_builder()


def test__len__():
    assert len(Svector.of([])) == 0
    assert len(Svector.of([1])) == 1
    assert len(Svector.empty()) == 0


def test_sum():
    assert len(Svector.of([])) == 0
    assert len(Svector.of([1])) == 1
    assert len(Svector.empty()) == 0


def test_no_mutate():
    with pytest.raises(TypeError):
        Svector.of([1, 2, 3])[0] = 1  # type: ignore


def test_fold_left():
    ...


def test_sort():
    assert Svector.of([1, 2, 3, 4]).sort_by(lambda x: x, reverse=True) == Svector.of([4, 3, 2, 1])

    class NotSortable:
        ...

    with pytest.raises(TypeError):
        Svector.of([NotSortable(), NotSortable()]).sort_by(lambda x: x)  # type: ignore


def test_max_by():
    assert Svector.of([1, 2, 3, 4]).max_by_option(lambda x: x) == 4

    @dataclass(frozen=True)
    class Something:
        field: int

    assert Svector.of([Something(field=1), Something(field=2)]).max_by_option(lambda x: x.field) == Something(field=2)


def test_pydantic_init():
    class TestModel(BaseModel):
        items: SvectorPydantic[int]

    my_instance = TestModel(items=Svector.of([1, 2, 3]))
    assert isinstance(my_instance.items, Svector)
    my_instance_list = TestModel(items=[1, 2, 3])
    assert isinstance(my_instance_list.items, Svector)


def test_group_by():
    assert Svector.of([1, 1, 2, 2, 4]).group_by(identity) == Svector(
        [(1, Svector([1, 1])), (2, Svector([2, 2])), (4, Svector([4]))]
    )
    assert Svector.of(["james", "james", "elliot"]).group_by(lambda x: x) == Svector(
        [('james', Svector(['james', 'james'])), ('elliot', Svector(['elliot']))]
    )


def test_group_by_dict():
    assert Svector.of([1, 1, 2, 2, 4]).group_by(lambda x: x).to_dict() == {
        1: Svector([1, 1]),
        2: Svector([2, 2]),
        4: Svector([4]),
    }
