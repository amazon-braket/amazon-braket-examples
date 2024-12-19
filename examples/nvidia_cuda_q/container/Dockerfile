FROM 292282985366.dkr.ecr.us-west-2.amazonaws.com/amazon-braket-pytorch-jobs:latest
RUN python3 -m pip install --upgrade pip

# install cudaq
ARG SCRIPT_PATH
ARG CUDAQ_PATH=/opt/conda/lib/python3.10/site-packages
ENV MPI_PATH=/opt/amazon/openmpi

RUN python3 -m pip install --no-cache --upgrade -r requirements-cuda.txt
RUN bash "${CUDAQ_PATH}/distributed_interfaces/activate_custom_mpi.sh"

# Setup our entry point
COPY "${SCRIPT_PATH}/braket_container.py" /opt/ml/code/braket_container.py
ENV SAGEMAKER_PROGRAM=braket_container.py
