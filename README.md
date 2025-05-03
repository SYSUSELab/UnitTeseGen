# UnitTeseGen
Automatically generate unit tests using LLM and context in the project

## Preparation
Environment for our experiments:
- Java: openjdk 17.0.12 2024-07-16
- Python: 3.13.0

## (demo) Running
1. rename `code/settings.py.template` to `code/settings.py` and compelete settings.
2. run the following commands:
```sh
cd code
# prepare datasets

# generate unit tests, use argument "--prepare_workspace" for the first time
python generate_unit_test.py --prepare_workspace
# run unit test and get coverage
python evaluation.py --operation coverage
```