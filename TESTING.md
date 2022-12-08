# Testing

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
mock setup `def pre_run(mock_utils):` passing in the mock_utils module as
the parameter. This function is where the notebook mocks can choose to
how to override the boto3 session, and what results to return. If the notebook
finishes executing all cells correctly `def post_run(tb):` will be called
for any cleanup and correctness testing (assertions that should be true
at the end of the notebook execution). 

By default, a notebook is run using the `default_mocks/default_mocks.py` which
uses the `default_data/default_capabilities.json` for returning device details
and `default_data/default_results.json` for all task results in the notebook.
This can be changed by adding a path in `test/integ_tests` that is identical
to the notebook being tested, with a file `<notebook name>_mocks.py` in that
directory. The file should specify `def pre_run(mock_utils):` and 
`def post_run(tb):`. If this file is found, it will be called instead of the
default mocks.


## Least Mock Testing
To run the integration tests for these notebooks using mocks to override
creation of tasks and jobs, just run:
```
pytest test/integ_tests -s --mock-level=LEAST test/integ_tests
```
These tests will require valid AWS account credentials to run.

### How it works

These tests work using the same mechanisms and use the same test data as provided
by "All Mock Testing", but only override functions in AwsSession that
create/get/cancel tasks and jobs. These tests take longer to run, but test
integration with braket services more thoroughly. 
