FROM 292282985366.dkr.ecr.us-west-2.amazonaws.com/amazon-braket-pytorch-jobs:latest
RUN python3 -m pip install --upgrade pip

# install cuda-quantum
ARG CUDA_QUANTUM_PATH=/opt/conda/lib/python3.10/site-packages
ENV MPI_PATH=/opt/amazon/openmpi
RUN python3 -m pip install cuda-quantum \
    && bash "${CUDA_QUANTUM_PATH}/distributed_interfaces/activate_custom_mpi.sh"

# install additional python dependencies
RUN python3 -m pip install --no-cache --upgrade -r requirements.txt

# Setup our entry point
ARG SCRIPT_PATH
COPY "$SCRIPT_PATH/braket_container.py" /opt/ml/code/braket_container.py
ENV SAGEMAKER_PROGRAM braket_container.py