# Welcome to OpenQAOA Jobs

This is still a dev-version of OpenQAOA jobs, so running the notebook requires following a few steps.


1. You will need to create a docker image containing OpenQAOA and upload it yo _your_ Amazon Elastic Container Registry. You can find more details here [https://docs.aws.amazon.com/braket/latest/developerguide/braket-jobs-byoc.html](https://docs.aws.amazon.com/braket/latest/developerguide/braket-jobs-byoc.html)

The OpenQAOA Dockerfile to use is

```dockerfile
FROM 292282985366.dkr.ecr.us-east-1.amazonaws.com/amazon-braket-pytorch-jobs:1.9.1-gpu-py38-cu111-ubuntu20.04

RUN git clone https://github.com/entropicalabs/openqaoa.git --branch feat_aws_jobs
RUN pip3 install /openqaoa/.
```

2. You need to install OpenQAOa. 
 - Create your desired virtual enviorement with a python version comprised between `3.7` and `3.11`
 - Git clone OpenQAOA, `git clone https://github.com/entropicalabs/openqaoa.git`
 - Then checkout the `feat_aws_jobs_no_pq` branch by typing `git checkout feat_aws_jobs_no_pq`
 - Install OpenQAOA: `pip install .`
 
3. Now you can run the 7_RQAOA_with_OpenQAOA_Jobs/RQAOA_with_OpenQAOA_Jobs.ipynb notebook :)

