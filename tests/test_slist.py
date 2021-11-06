import timeit

import pytest
from pyrsistent.typing import PVector

from svector.immutable_list import Slist, Cons, NilSingleton
from svector.immutable_tree import Svector
from svector.type_definitions import A_co


def test_of():
    assert Slist.of([1, 2, 3]).to_list() == [1, 2, 3]
    assert Slist.of([]).to_list() == []
    assert Slist.empty().to_list() == []
    assert Slist.of(item for item in range(1, 5)).to_list() == [1, 2, 3, 4]


def test_length():
    assert Slist.of([1, 2, 3]).length == 3
    assert Slist.of([]).length == 0


def test_head():
    assert Slist.of([1, 2, 3]).head == 1
    assert Slist.of([1, 2, 3]).tail == Slist.of([2, 3])

    with pytest.raises(IndexError):
        Slist.of([]).head


def test_tail():
    assert Slist.of([1]).tail == NilSingleton
    assert Slist.of([1]).tail == Slist.of([])


def test_map():
    assert Slist.of([1, 2, 3]).map(lambda x: x * 3) == Slist.of([3, 6, 9])
    assert Slist.of([]).map(lambda x: x * 3) == Slist.of([])


def test_flatten_list():
    assert Slist.of([[1], [2, 2], [3, 3, 3]]).flatten_iter() == Slist.of([1, 2, 2, 3, 3, 3])
    assert Slist.of([[], [2, 2], [3, 3, 3]]).flatten_iter() == Slist.of([2, 2, 3, 3, 3])  # type:ignore


def test_is_empty():
    assert Slist.of([123]).is_empty is False
    assert Slist.of([]).is_empty is True


def test_take():
    assert Slist.of([]).take(1) == Slist.of([])
    assert Slist.of([1, 2, 3]).take(0) == Slist.of([])
    assert Slist.of([1, 2, 3]).take(1) == Slist.of([1])
    assert Slist.of([1, 2, 3]).take(2) == Slist.of([1, 2])
    assert Slist.of([1, 2, 3]).take(3) == Slist.of([1, 2, 3])


def test_prepend():
    assert Slist.of([]).prepend(0) == Slist.of([0])
    assert Slist.of([]).prepend(1).prepend(2) == Slist.of([2, 1])


def test_extend():
    assert Slist.of([]).extend([1, 2, 3]) == Slist.of([3, 2, 1])
    assert Slist.of([1]).extend(["boban", "gloria"]) == Slist.of(["gloria", "boban", 1])


def test__init__():
    assert Slist.new(1, 2, 3) == Slist.of([1, 2, 3])


def test__len__():
    assert len(Slist.of([])) == 0
    assert len(Slist.of([1])) == 1
    assert len(Slist.empty()) == 0


from pyrsistent import v, l, plist

#
# def test__pyrsistent() -> None:
#     items = 10000
#
#     vec = Svector(i for i in range(items))
#     time_vec = timeit.timeit(lambda: vec.map(lambda x: x * 3), number=1000)
#
#     slist = Slist.of(i for i in range(items))
#     time_slist = timeit.timeit(lambda: slist.map(lambda x: x * 3), number=1000)
#
#     pyrsist_list: PVector[int] = v(*(i for i in range(1, items)))
#     time_pyrsist = timeit.timeit(lambda: v(*(i * 3 for i in pyrsist_list)), number=1000)
#     py_list = [i for i in range(1, items)]
#     time_python = timeit.timeit(lambda: [i * 3 for i in py_list], number=1000)
#     assert False, f"Slist:{time_slist} vs SVec{time_vec} vs Pyrsistent{time_pyrsist} vs StdList{time_python}"
