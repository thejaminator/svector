from functools import reduce
from typing import Final, Union, overload, Callable, Iterable, Optional, Sequence, Generic
import concurrent.futures

import pyrsistent
from pyrsistent.typing import PVector, PVectorEvolver
from pyrsistent._pvector import PVector as PVectorABC

from svector.type_definitions import A_co, B, CanCompare, CanHash


def vec(*args: B) -> "Svector[B]":
    """
    Convienient function to instantiate a Svector by passing multiple args instead of an iterable
    Equivalent:
    >>> vec(1,2,3)
    Svector([1,2,3])
    >>> Svector.of([1,2,3])
    Svector([1,2,3])
    """
    return Svector.of(args)


class Svector(Sequence[A_co]):
    def __init__(self, iterable: Iterable[A_co]):
        self.__data: Final[PVector[A_co]] = pyrsistent.pvector(iterable)

    @staticmethod
    def from_pvector(vec: PVector[B]) -> "Svector[B]":
        return Svector(vec)

    @staticmethod
    def of(iterable: Iterable[A_co]) -> "Svector[A_co]":
        return Svector(iterable)

    @staticmethod
    def empty() -> "Svector[A_co]":
        return Svector.of([])

    """Expose standard pyrsistent methods
    TODO: Maybe extend PVectorABC itself?"""

    @overload
    def __getitem__(self, i: int) -> A_co:
        pass

    @overload
    def __getitem__(self, i: slice) -> "Svector[A_co]":
        pass

    def __getitem__(self, i: Union[int, slice]) -> "Union[A_co, Svector[A_co]]":
        if isinstance(i, int):
            return self.__data.__getitem__(i)
        else:
            return Svector(self.__data.__getitem__(i))

    def __len__(self) -> int:
        return len(self.__data)

    def __eq__(self, other) -> bool:
        return self.__data == other

    def __repr__(self):
        return f"SVector({list(self.__data)})"

    def __iter__(self):
        return iter(self.__data)

    def __hash__(self) -> int:
        return self.__data.__hash__()

    def append(self, val: B) -> "Svector[Union[A_co, B]]":
        # Type stubs of Pyrsistent are wrong, they assume stuff you have has to be A_co rather than something wider.
        return Svector(self.__data.append(val))  # type: ignore

    def delete(self, index: int, stop: Optional[int]) -> "Svector[A_co]":
        return Svector(self.__data.delete(index=index, stop=stop))

    def extend(self, obj: Iterable[B]) -> "Svector[Union[A_co,B]]":
        return Svector(self.__data.extend(obj))  # type: ignore

    def tolist(self) -> list[A_co]:
        return self.to_list()

    def mset(self, *args: Iterable[Union[A_co, int]]) -> "Svector[A_co]":
        return Svector(self.__data.mset(*args))

    def remove(self, value: B) -> "Svector[A_co]":
        """Removes an element equal to the value"""
        return Svector(self.__data.remove(value=value))  # type: ignore

    def set(self, i: int, val: B) -> "Svector[Union[A_co, B]]":
        """Sets an element at the index"""
        return Svector(self.__data.set(i=i, val=val))  # type: ignore

    """Exetensions"""

    @staticmethod
    def new_builder() -> "SvectorBuilder[A_co]":
        return SvectorBuilder()

    def to_list(self) -> list[A_co]:
        return [item for item in self]

    @property
    def not_empty(self) -> bool:
        return len(self) > 0

    @property
    def is_empty(self) -> bool:
        return len(self) == 0

    @property
    def length(self) -> int:
        return len(self)

    def map(self, func: Callable[[A_co], B]) -> "Svector[B]":
        return Svector.of(func(item) for item in self)

    def map_enumerate(self, func: Callable[[int, A_co], None]):
        return Svector.of(func(idx, item) for idx, item in enumerate(self))

    def filter(self, predicate: Callable[[A_co], bool]) -> "Svector[A_co]":
        return Svector.of(item for item in self if predicate(item))

    def flatten_option(self: "Svector[Optional[B]]") -> "Svector[B]":
        return Svector.of(item for item in self if item is not None)

    def flat_map_option(self, func: Callable[[A_co], Optional[B]]) -> "Svector[B]":
        """Runs the provided function, and filters out the Nones"""
        return self.map(func).flatten_option()

    def flatten_iter(self: "Svector[Iterable[B]]") -> "Svector[B]":
        """Flattens a nested iterable
        >>> Svector.of([[1], [2, 2], [3, 3, 3]]).flatten_iter()
        Svector.of([1, 2, 2, 3, 3, 3])
        """
        return Svector.of(item for sublist in self for item in sublist)

    def for_each(self, func: Callable[[A_co], None]) -> "Svector[A_co]":
        """Runs an effect on each element, and returns the original list
        e.g. SVector.of([1,2,3]).foreach(print)"""
        for item in self:
            func(item)
        return self

    def for_each_enumerate(self, func: Callable[[int, A_co], None]) -> "Svector[A_co]":
        """Runs an effect on each element, and returns the original list
        e.g. SVector.of([1,2,3]).foreach(print)"""
        for idx, item in enumerate(self):
            func(idx, item)
        return self

    def get_or_else(self, index: int, orElse: B) -> Union[A_co, B]:
        try:
            return self.__getitem__(index)
        except IndexError:
            return orElse

    def find_one(self, predicate: Callable[[A_co], bool]) -> Optional[A_co]:
        for item in self:
            if predicate(item):
                return item
        return None

    def find_one_or_raise(self, predicate: Callable[[A_co], bool], exception: Exception) -> A_co:
        result = self.find_one(predicate=predicate)
        if result is not None:
            return result
        else:
            raise exception

    def find_one_idx(self, predicate: Callable[[A_co], bool]) -> Optional[int]:
        for idx, item in enumerate(self):
            if predicate(item):
                return idx
        return None

    def take(self, n: int) -> "Svector[A_co]":
        return self[:n]

    def sort(self: "Svector[CanCompare]", reverse: bool = False) -> "Svector[CanCompare]":
        """
        Mypy does not typecheck properly until https://github.com/python/mypy/issues/11167 is resolved
        Use sort_by(lambda x: x) for a version that properly typechecks
        """
        return Svector.of(sorted(self, reverse=reverse))

    def sort_by(self, key: Callable[[A_co], CanCompare], reverse: bool = False) -> "Svector[A_co]":
        """
        Sorts by the given key
        >>> Svector.of([1, 2, 3, 4]).sort_by(lambda x: x, reverse=True)
        Svector([4, 3, 2, 1])
        """
        return Svector.of(sorted(self, key=key, reverse=reverse))

    @property
    def distinct(self: "Svector[CanHash]") -> "Svector[CanHash]":
        """Deduplicates items. Preserves order.
        Mypy does not typecheck properly until https://github.com/python/mypy/issues/11167 is resolved
        use distinct_by(lambda x: x) for a version that properly typechecks"""
        seen = set()
        output = []
        for item in self:
            if item in seen:
                continue
            else:
                seen.add(item)
                output.append(item)
        return Svector.of(output)

    def distinct_by(self, key: Callable[[A_co], CanHash]) -> "Svector[A_co]":
        """Deduplicates a list by a key. Preserves order."""
        seen = set()
        output = []
        for item in self:
            item_hash = key(item)
            if item_hash in seen:
                continue
            else:
                seen.add(item_hash)
                output.append(item)
        return Svector.of(output)

    def par_map(self, func: Callable[[A_co], B], executor: concurrent.futures.Executor) -> "Svector[B]":
        """Applies the function to each element using the specified executor. Awaits for all results.
        If executor is ProcessPoolExecutor, make sure the function passed is pickable, i.e. use functools partial instead of lambda functions"""
        futures: list[concurrent.futures._base.Future[B]] = [executor.submit(func, item) for item in self]
        results = []
        for fut in futures:
            results.append(fut.result())
        return Svector.of(results)

    """Reduce methods"""

    def sum(
        self: "Svector[float]",
    ) -> Union[float]:
        """Returns 0 when the list is empty"""
        return sum(self)

    def max_by_option(self, key: Callable[[A_co], CanCompare]) -> Optional[A_co]:
        if self.not_empty:
            return max(self, key=key)
        else:
            return None

    def min_by_option(self, key: Callable[[A_co], CanCompare]) -> Optional[A_co]:
        if self.not_empty:
            return min(self, key=key)
        else:
            return None

    @property
    def first_option(self) -> Optional[A_co]:
        if self.not_empty:
            return self[0]

        else:
            return None

    @property
    def last_option(self) -> Optional[A_co]:
        if self.not_empty:
            return self[-1]

        else:
            return None

    def fold_left(self, acc: B, func: Callable[[B, A_co], B]) -> B:
        return reduce(func, self, acc)

    def mk_string(self: "Svector[str]", sep: str) -> str:
        return sep.join(self)

    """Methods for compat with pydantic"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field):  # field: ModelField
        subfield = field.sub_fields[0]  # e.g. the int type in Svector[int]
        if not isinstance(v, list):
            raise TypeError(f"list required to instantiate a Svector, got {v} of type {type(v)}")
        validated_values = []
        for idx, item in enumerate(v):
            valid_value, error = subfield.validate(item, {}, loc=str(idx))
            if error is not None:
                raise ValueError(f"Error validating {item}, Error: {error}")

            validated_values.append(valid_value)
        return Svector.of(validated_values)


class SvectorBuilder(Generic[B]):
    def __init__(self):
        self.__data: list[B] = []

    def add(self, item: B) -> None:
        self.__data.append(item)

    def add_all(self, iterable: Iterable[B]) -> None:
        for item in iterable:
            self.add(item)

    def result(self) -> Svector[B]:
        return Svector.of(self.__data)
