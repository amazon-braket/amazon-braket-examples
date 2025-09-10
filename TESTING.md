# Testing

We use a series of tests for the example notebooks. For formatting, you can run `hatch run lint:style`. Additionally, you should run the integration tests as below. There also are build tests for python 3.9, 3.10, and 3.11, so if you are using any of these you have a greater chance of success.  

## All Mock Testing
To run the integration tests for these notebooks using mocks to override
calls to AWS, just run:
```
pytest test/integ_tests
```
These tests do not require AWS account credentials to run.

### How it works

We use testbook to call each notebook and mock out all calls to the boto3 by
overwriting the boto3.Session class. We then provide default results that would
have been returned by a boto3 client. 

We inject `mock_utils.py` at the beginning of each notebook, then call the
mock setup `def pre_run_inject(mock_utils):` passing in the mock_utils module as
the parameter. This function is where the notebook mocks can choose to
how to override the boto3 session, and what results to return. If the notebook
finishes executing all cells correctly `def post_run(tb):` will be called
for any cleanup and correctness testing (assertions that should be true
at the end of the notebook execution). 

By default, a notebook is run using the `default_mocks/default_mocks.py` which
uses the `default_data/default_capabilities.json` for returning device details
and `default_data/default_results.json` for all quantum task results in the notebook.
This can be changed by adding a path in `test/integ_tests` that is identical
to the notebook being tested, with a file `<notebook name>_mocks.py` in that
directory. The file should specify `def pre_run_inject(mock_utils):` and 
`def post_run(tb):`. If this file is found, it will be called instead of the
default mocks.


## Least Mock Testing
To run the integration tests for these notebooks using mocks to override
creation of quantum tasks and hybrid jobs, just run:
```
pytest test/integ_tests -s --mock-level=LEAST test/integ_tests
```
These tests will require valid AWS account credentials to run.

### How it works

These tests work using the same mechanisms and use the same test data as provided
by "All Mock Testing", but only override functions in AwsSession that
create/get/cancel quantum tasks and hybrid jobs. These tests take longer to run, but test
integration with braket services more thoroughly. 

## Recording
It is possible to use our test framework to record some calls that are made
to Braket using the code below.

Create a code cell at the top of the notebook with the following code:
```python
import os
record_path = None
curr_path = ".."
while record_path == None:
    files = os.listdir(curr_path)
    if "TESTING.md" in files:
        record_path = os.path.join(curr_path, "test", "integ_tests", "record_utils.py")
        break
    curr_path = os.path.join("..", curr_path)
from importlib.machinery import SourceFileLoader
record_utils = SourceFileLoader("notebook_record_utils", record_path).load_module()
```
Running the entire notebook will generate several files, which can then be used
for playback.

## Playback

Simply append the following line to the code cell specified in the Recording section
```
record_utils.playback()
```
Re-running the notebook will use the generated files made during recording.

## Testing commented code

In the example notebooks, some code cells are presented as commented out to prevent accidental execution of costly or long-running operations, particularly those that run on a QPU. However, commented code can become prone to errors over time due to lack of regular testing.

To improve test coverage, we introduce a special flag: `## UNCOMMENT_TO_RUN`. As a developer, you can include this flag within a cell to mark the beginning of a block that should be uncommented during integration testing. The integration test framework will detect the `## UNCOMMENT_TO_RUN` marker and automatically uncomment all subsequent lines until it encounters a line that is not commented.

To ensure this process works correctly:
- Use a single `#` for code comments that should be uncommented during testing.
- Use double `##` for non-code, descriptive comments that should remain commented (and not be treated as executable code).

Following this convention allows the integration test system to selectively and safely test example notebooks without risking unintended costly runs in normal usage.

