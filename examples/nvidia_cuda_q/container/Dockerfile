FROM 292282985366.dkr.ecr.us-west-2.amazonaws.com/amazon-braket-base-jobs:latest

ARG SCRIPT_PATH
ARG CUDAQ_PATH=/usr/local/lib/python3.10/site-packages

ENV MPI_PATH=/usr/local \
    SAGEMAKER_PROGRAM=braket_container.py

# install Python dependencies including cudaq
COPY "${SCRIPT_PATH}/requirements.txt" .
RUN pip install --no-cache --upgrade -r requirements.txt && \
    bash "${CUDAQ_PATH}/distributed_interfaces/activate_custom_mpi.sh"

# setup the entry point  
COPY "${SCRIPT_PATH}/braket_container.py" /opt/ml/code/braket_container.py
