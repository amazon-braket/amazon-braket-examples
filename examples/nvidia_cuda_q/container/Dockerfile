FROM 292282985366.dkr.ecr.us-west-2.amazonaws.com/amazon-braket-base-jobs:latest

ARG SCRIPT_PATH

# install cudaq
ENV MPI_PATH=/usr/local
RUN pip install cudaq mpi4py
RUN bash /usr/local/lib/python3.10/site-packages/distributed_interfaces/activate_custom_mpi.sh

# install additional python dependencies
COPY "${SCRIPT_PATH}/requirements.txt" .
RUN pip install --no-cache --upgrade -r requirements.txt

# setup the entry point
COPY "${SCRIPT_PATH}/braket_container.py" /opt/ml/code/braket_container.py
ENV SAGEMAKER_PROGRAM=braket_container.py