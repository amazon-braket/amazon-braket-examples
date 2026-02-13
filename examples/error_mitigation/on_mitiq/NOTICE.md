## Installing and using Mitiq 

*[Mitiq](https://mitiq.readthedocs.io/en/stable/)* is licensed under the ***[GNU GPLv3](https://github.com/unitaryfoundation/mitiq/blob/main/LICENSE)*** license, and Mitiq is <u>**not**</u> distributed or installed by default using standard installation scripts. 

To install, run `pip install mitiq`, follow the local installation script in the relevant notebooks, or run 
`pip install -r requirements.txt` followed by `pip install -r /extra/requirements-mitiq.txt` from the head folder. 

### Contributing

If contributing to the Mitiq examples, do not include *Mitiq* as a requirement in requirements.txt. 

All Mitiq related files and imports should remain in the `examples/error_mitigation/on_mitiq` folder, as the testing environment. 

>[!WARNING]
>The files in the directory are **examples** of how to use *Mitiq* with Amazon Braket. Please be careful when referencing code.

### Testing examples

The Mitiq examples are tested in their own hatch environment. To run their tests, use:
```
hatch env create mitiq-test 
hatch run test-mitiq:test
```

To add a test to these examples, use the pytest marker. 
```
@pytest.mark.mitiq
def test_some_random_method():
    ...
```

Finally, do not put Mitiq as a top-level import in any testing file - this will fail the main testing environment. 