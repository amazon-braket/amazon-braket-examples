
---

## <a name="support ">Support</a>

### Installing Dependencies 

To install the dependencies required for running the notebook examples in this repository you can create a conda environment with below commands.

```bash
conda env create -n <your_env_name> -f environment.yml
```

Activate the conda environment using:
ß
```bash
conda activate <your_env_name>
```

To remove the conda environment use:

```bash
conda deactivate
```

For more information, please see [conda usage](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)

To run the notebook examples locally on your IDE, first, configure a profile to use your account to interact with AWS. To learn more, see [Configure AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

After you create a profile, use the following command to set the `AWS_PROFILE` so that all future commands can access your AWS account and resources.

```bash
export AWS_PROFILE=YOUR_PROFILE_NAME
```

### Issues and Bug Reports

If you encounter bugs or face issues while using the examples, please let us know by posting
the issue on our [Github issue tracker](https://github.com/amazon-braket/amazon-braket-examples/issues/).  
For other issues or general questions, please ask on the [Quantum Computing Stack Exchange](https://quantumcomputing.stackexchange.com/questions/ask) and add the tag [amazon-braket](https://quantumcomputing.stackexchange.com/questions/tagged/amazon-braket).

### Feedback and Feature Requests

If you have feedback or features that you would like to see on Amazon Braket, we would love to hear from you!  
[Github issues](https://github.com/amazon-braket/amazon-braket-examples/issues/) is our preferred mechanism for collecting feedback and feature requests, allowing other users
to engage in the conversation, and +1 issues to help drive priority.
