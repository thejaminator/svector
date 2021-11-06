import pytest

from svector.immutable_tree import Svector


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
    assert Svector.of([[], [2, 2], [3, 3, 3]]).flatten_iter() == Svector.of([2, 2, 3, 3, 3]) # type: ignore


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
        Svector.of([1, 2, 3])[0] = 1


def test_fold_left():
    ...

def test_sort():
    class NotSortable:
        ...

    assert Svector.of([NotSortable()]).sort_by(lambda x: x)

