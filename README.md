# UnitTeseGen
Automatically generate unit tests using LLM and context in the project

## Preparation
Environment for our experiments:
- Java: openjdk 11.0.26 2025-01-21
- Python: 3.13.0

**Note:** If you use a lower version of the Java Runtime Environment than us, please repackage the jar file in `code/java`. Taking folder `project-info-extract` as example:

```sh
cd code/java/project-info-extract
jar -cvfe ../project-info-extract.jar Test -C target . -C lib .
# this also work
jar cfm ../project-info-extract.jar MANIFEST.MF -C target . -C lib .
```

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