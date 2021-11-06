from slist.immutable_tree import Svector


def test_map():
    assert Svector.of([1, 2, 3]).map(lambda x: x * 3) == Svector.of([3, 6, 9])
    assert Svector.of([]).map(lambda x: x * 3) == Svector.of([])