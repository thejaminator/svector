import concurrent.futures
from functools import reduce
from typing import (
    Generic,
    Optional,
    Final,
    Iterable,
    Any,
    Sequence,
    Iterator,
    overload,
    Union,
    NoReturn,
    Callable,
)
from abc import abstractmethod
from collections import abc

from svector.type_definitions import A_co, B, CanCompare, CanHash


class Slist(abc.Sequence[A_co]):
    # Some help from https://github.com/tobgu/pyrsistent/blob/master/pyrsistent/_plist.py

    @property
    @abstractmethod
    def is_empty(self) -> bool:
        ...

    @property
    @abstractmethod
    def head(self) -> Union[A_co, NoReturn]:
        """Raises excpetion if empty list"""
        ...

    @property
    @abstractmethod
    def tail(self) -> "Union[Slist[A_co], NoReturn]":
        """Raises excpetion if empty list"""
        ...

    @staticmethod
    def new(*args: B) -> "Slist[B]":
        """Constructs a Slist from argumetns
        TODO:Find out if we can hack __new__ to do this
        >>> Slist.new(1,2,3)
        """
        return Slist.of(args)

    @staticmethod
    def of(iterable: Iterable[A_co]) -> "Slist[A_co]":
        """Constructs a Slist from an iterable
        >>> Slist.of([1,2,3])
        """
        # Only accept list because reversing a list is more straightforward then any Iterable...
        if isinstance(iterable, list):
            previous_item: Slist[A_co] = NilSingleton
            for item in iterable[::-1]:
                next_item = Cons(head=item, tail=previous_item)
                previous_item = next_item
            return previous_item

        elif isinstance(iterable, Slist):
            # Yay immutability!
            return iterable

        else:
            return Slist.of(list(iterable))

    @overload
    def __getitem__(self, i: int) -> A_co:
        pass

    @overload
    def __getitem__(self, i: slice) -> "Slist[A_co]":
        pass

    def __getitem__(self, i: Union[int, slice]) -> "Union[A_co, Slist[A_co]]":
        """Try not to slice alot, its rather inefficient mate"""
        if isinstance(i, int):
            if i < 0:
                raise ValueError(f"Positive index required, got {i}")
            else:
                current_idx = 0
                current_item: Slist[A_co] = self
                while True:
                    if current_item is NilSingleton:
                        raise IndexError(f"Index exceeds length of list!")
                    if current_idx == i:
                        break
                    current_item: Slist[A_co] = current_item.tail  # type: ignore
                    current_idx += 1

                return current_item.head
        else:
            # TODO: Less dumb way
            return Slist.of(self.to_list().__getitem__(i))

    @staticmethod
    def empty() -> "Slist[A_co]":
        return Slist.of([])

    def __iter__(self) -> Iterator[A_co]:
        current_item = self
        while current_item is not NilSingleton:
            yield current_item.head
            current_item = current_item.tail

    def __repr__(self):
        return f"Slist({list(self)})"

    def __eq__(self, other: Any) -> bool:
        # TODO: can make this faster
        if isinstance(other, Slist):
            return self.to_list() == other.to_list()
        else:
            return False

    def prepend(self, item: B) -> "Slist[Union[A_co, B]]":
        return Cons(head=item, tail=self)

    def __add__(self, other: B) -> "Slist[Union[A_co, B]]":
        """Alias for prepend"""
        return self.prepend(other)

    def extend(self, iterable: Iterable[B]) -> "Slist[Union[A_co, B]]":
        previous_item: Slist[A_co] = self
        for item in iterable:
            previous_item: Slist[Union[A_co, B]] = previous_item.prepend(item)  # type: ignore
        return previous_item

    def to_list(self) -> list[A_co]:
        return [item for item in self]

    @property
    def not_empty(self) -> bool:
        return len(self) > 0

    @property
    def length(self) -> int:
        return len(self)

    def map(self, func: Callable[[A_co], B]) -> "Slist[B]":
        return Slist.of(func(item) for item in self)

    def filter(self, predicate: Callable[[A_co], bool]) -> "Slist[A_co]":
        return Slist.of(item for item in self if predicate(item))

    def flatten_option(self: "Slist[Optional[B]]") -> "Slist[B]":
        return Slist.of(item for item in self if item is not None)

    def flat_map_option(self, func: Callable[[A_co], Optional[B]]) -> "Slist[B]":
        """Runs the provided function, and filters out the Nones"""
        return self.map(func).flatten_option()

    def flatten_iter(self: "Slist[Iterable[B]]") -> "Slist[B]":
        return Slist.of(item for sublist in self for item in sublist)

    def for_each(self, func: Callable[[A_co], None]) -> "Slist[A_co]":
        """Runs an effect on each element, and returns the original list
        e.g. Slist.of([1,2,3]).foreach(print)"""
        for item in self:
            func(item)
        return self

    def for_each_enumerate(self, func: Callable[[int, A_co], None]) -> "Slist[A_co]":
        """Runs an effect on each element, and returns the original list
        e.g. Slist.of([1,2,3]).foreach(print)"""
        for idx, item in enumerate(self):
            func(idx, item)
        return self

    def get(self, index: int, orElse: B) -> Union[A_co, B]:
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

    def take(self, n: int) -> "Slist[A_co]":
        if n < 0:
            raise ValueError(f"Method take was called with a negative n: {n}")
        elif n == 0 or self.is_empty:
            return NilSingleton
        else:
            next: Slist[A_co] = self.tail
            acc: list[A_co] = [self.head]
            while True:
                if next.is_empty:
                    break
                if len(acc) < n:
                    acc.append(next.head)
                    next = next.tail
                else:
                    break

            return Slist.of(acc)

    def sort_by(self, key: Callable[[A_co], CanCompare], reverse: bool = False) -> "Slist[A_co]":
        """
        Mypy does not typecheck properly until https://github.com/python/mypy/issues/11167 is resolved
        Use sort_by(lambda x: x) to sort by the element.
        """
        return Slist.of(sorted(self, key=key, reverse=reverse))

    @property
    def distinct(self: "Slist[CanHash]") -> "Slist[CanHash]":
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
        return Slist.of(output)

    def distinct_by(self, key: Callable[[A_co], CanHash]) -> "Slist[A_co]":
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
        return Slist.of(output)

    def par_map(self, func: Callable[[A_co], B], executor: concurrent.futures.Executor) -> "Slist[B]":
        """Applies the function to each element using the specified executor. Awaits for all results.
        If executor is ProcessPoolExecutor, make sure the function passed is pickable, i.e. use functools partial instead of lambda functions"""
        futures: list[concurrent.futures._base.Future[B]] = [executor.submit(func, item) for item in self]
        results = []
        for fut in futures:
            results.append(fut.result())
        return Slist.of(results)

    """Reduce methods"""

    def sum(
        self: "Slist[float]",
    ) -> Union[float]:
        """Returns 0 when the list is empty"""
        return sum(self)

    def fold_left(self, acc: B, func: Callable[[B, A_co], B]) -> B:
        return reduce(func, self, acc)


class Nil(Slist[A_co]):
    @property
    def head(self) -> NoReturn:
        raise IndexError("head of empty list")

    @property
    def tail(self) -> NoReturn:
        raise IndexError("tail of empty list")

    @property
    def is_empty(self) -> bool:
        return True

    def __len__(self) -> int:
        return 0


NilSingleton = Nil[Any]()


class Cons(Slist[A_co]):
    def __init__(self, head: A_co, tail: Slist[A_co]):
        self.__head: Final = head
        self.__tail: Final = tail  # TODO: add immutability
        self.__length: Final = tail.length + 1

    @property
    def is_empty(self) -> bool:
        return False

    @property
    def head(self) -> A_co:
        return self.__head

    @property
    def tail(self) -> Slist[A_co]:
        return self.__tail

    def __len__(self) -> int:
        return self.__length


class ListBuilder(Generic[B]):
    def __init__(self):
        self.__data: list[B] = []

    def add_one(self, item: B) -> None:
        self.__data.append(item)

    def add_all(self, iterable: Iterable[B]) -> None:
        for item in iterable:
            self.add_one(item)

    def to_slist(self) -> Slist[B]:
        return Slist.of(self.__data)
