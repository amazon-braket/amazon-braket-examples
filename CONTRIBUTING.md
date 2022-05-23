# Contributing Guidelines

Thank you for your interest in contributing to our project. Whether it's a bug report, new example, or correction, we greatly value feedback and contributions from our community.

Please read through this document before submitting any issues or pull requests to ensure we have all the necessary
information to effectively respond to your bug report or contribution.


## Table of Contents

* [Report Bugs](#report-bugs)
* [Contribute via Pull Requests (PRs)](#contribute-via-pull-requests-prs)
  * [Pull Down the Code](#pull-down-the-code)
  * [Making your Changes](#making-your-changes)
  * [Send a Pull Request](#send-a-pull-request)
* [Code of Conduct](#code-of-conduct)
* [Security Issue Notifications](#security-issue-notifications)
* [Licensing](#licensing)

## Report Bugs

We welcome you to use the GitHub issue tracker to report bugs.

When filing an issue, please check [existing open](https://github.com/aws/amazon-braket-examples/issues) and [recently closed](https://github.com/aws/amazon-braket-examples/issues?q=is%3Aissue+is%3Aclosed) issues to make sure somebody else hasn't already
reported the issue. Please try to include as much information as you can. Details like these are incredibly useful:

* A reproducible test case or series of steps.
* The version of our code being used.
* Any modifications you've made relevant to the bug.
* A description of your environment or deployment.


## Contribute via Pull Requests (PRs)

Contributions via pull requests are much appreciated.

Before sending us a pull request, please ensure that:

* You are working against the latest source on the *main* branch.
* You check the existing open and recently merged pull requests to make sure someone else hasn't already addressed the problem or created a similar example.
* You open an issue to discuss any significant work - we would hate for your time to be wasted.


### Pull Down the Code

1. If you do not already have one, create a GitHub account by following the prompts at [Join Github](https://github.com/join).
1. Create a fork of this repository on GitHub. You should end up with a fork at `https://github.com/<username>/amazon-braket-examples`.
   1. Follow the instructions at [Fork a Repo](https://help.github.com/en/articles/fork-a-repo) to fork a GitHub repository.
1. Clone your fork of the repository: `git clone https://github.com/<username>/amazon-braket-examples` where `<username>` is your github username.


### Making your changes
When you make a contribution please ensure that you
1. Follow the existing flow of a notebook ([example](https://github.com/aws/amazon-braket-examples/blob/main/examples/getting_started/1_Running_quantum_circuits_on_simulators.ipynb)).
1. Do not duplicate existing information but refer to other examples as relevant.
1. Only have Open Source licensed dependencies in your example.
1. Ensure that your example runs without issues on both a recent Braket Notebook Instance (create a new Braket Notebook Instance or restart one from Amazon Braket [in the console](https://docs.aws.amazon.com/braket/latest/developerguide/braket-get-started-create-notebook.html)) and locally, using our most [recently released Amazon Braket SDK version](https://github.com/aws/amazon-braket-sdk-python/blob/main/README.md#installing-the-amazon-braket-python-sdk). Run the entire notebook by clicking `Cells > Run All`, either in the console or locally, and confirm that every cell completes without error.
1. Ensure that you are using HTML elements to source images in the notebooks, and that sourced images are saved in the appropriate example folder.
### Send a Pull Request

GitHub provides additional documentation on [Creating a Pull Request](https://help.github.com/articles/creating-a-pull-request/).

Please remember to:
* Use commit messages (and PR titles) that follow best practices on [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/) for guidance.
* Send us a pull request.

## Code of Conduct

This project has adopted the [Amazon Open Source Code of Conduct](https://aws.github.io/code-of-conduct).
For more information see the [Code of Conduct FAQ](https://aws.github.io/code-of-conduct-faq) or contact
opensource-codeofconduct@amazon.com with any additional questions or comments.


## Security Issue Notifications

If you discover a potential security issue in this project we ask that you notify AWS/Amazon Security via our [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public github issue.


## Licensing

See the [LICENSE](https://github.com/aws/amazon-braket-examples/blob/main/LICENSE) file for our project's licensing. We will ask you to confirm the licensing of your contribution.

We may ask you to sign a [Contributor License Agreement (CLA)](http://en.wikipedia.org/wiki/Contributor_License_Agreement) for larger changes.