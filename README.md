# Svector

Svector (pronounced Swag-tor) provides extension methods to pyrsistent data structures. 
Easily chain your methods confidently with tons of additional methods. Leverage 
the latest mypy features to spot errors during coding.


[![pypi](https://img.shields.io/pypi/v/svector.svg)](https://pypi.org/project/svector)
[![python](https://img.shields.io/pypi/pyversions/svector.svg)](https://pypi.org/project/svector)
[![Build Status](https://github.com/thejaminator/svector/actions/workflows/dev.yml/badge.svg)](https://github.com/thejaminator/svector/actions/workflows/dev.yml)

```
pip install svector
```

Immutable list replacement for python. With postfix methods for easy functional programming.


* GitHub: <https://github.com/thejaminator/svector>


## Quick Start
With mypy installed, easily spot errors when you call the wrong methods on your sequence.

```python
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
```

Svector provides methods that you can chain easily for easier data processing.
```python
from svector import Svector

Svector.of([-1, 0, 1]).map(
    lambda x: x if x >= 0 else None).flatten_option()  # Mypy infers Svector[int] correctly

result = (
    Svector.of(i for i in range(5000))
    .map(lambda x: (x % 3, x))
    .filter(lambda x: x[0] == 0)
    .for_each_enumerate(lambda idx, element: print(f"{idx}: {element}"))
    .take(5)
)
```


## Methods
Svector is heavily influenced by Scala, hence the S.
