##
Run tests
```
pytest
```

Run builds
```
poetry install -E doc -E dev -E test
poetry run tox
```


To do:
- Add pydantic support
- Add docs
- Add quickstart
- Add other scala list methods
- Add parmap_coroutine
- Add benchmarks
- Add mutation checks
- Support Maybe Monad / flupy