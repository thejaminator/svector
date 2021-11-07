from typing import TypeVar, Hashable, Protocol

A_co = TypeVar("A_co", covariant=True)
B = TypeVar("B")
CanCompare = TypeVar("CanCompare", bound="Comparable")
CanHash = TypeVar("CanHash", bound=Hashable)


class Comparable(Protocol):
    def __lt__(self: CanCompare, other: CanCompare) -> bool:
        pass


def identity(item: B) -> B:
    return item
