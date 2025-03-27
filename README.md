# UnitTeseGen
Automatically generate unit tests using LLM and context in the project

## (demo) Running
```sh
cd code
# prepare datasets

# generate unit tests, use argument "--prepare_workspace" for the first time
python generate_unit_test.py --prepare_workspace
# run unit test and get coverage
python evaluation.py --operation coverage
```