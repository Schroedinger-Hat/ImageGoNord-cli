# Tests folder

To run tests, see [setup](../README.md) and run

```bash
~$ python3 -m unittest discover ./tests
```

To run specific types of tests, for example unit test run

```bash
~$ python3 -m unittest discover ./tests/unit
```

To validate the CLI contract examples in [README](../README.md), run:

```bash
~$ python3 -m unittest tests.unit.test_readme_cli_contract_consistency
```
