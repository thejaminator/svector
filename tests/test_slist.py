import timeit

import pytest

from slist.immutable_list import Slist, Cons, NilSingleton, A_co


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
    assert Slist.args(1, 2, 3) == Slist.of([1, 2, 3])
