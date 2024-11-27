FROM 292282985366.dkr.ecr.us-west-2.amazonaws.com/amazon-braket-pytorch-jobs:latest
RUN python3 -m pip install --upgrade pip

# install cuda-quantum
ARG SCRIPT_PATH
ARG CUDAQ_PATH=/opt/conda/lib/python3.10/site-packages
ENV MPI_PATH=/opt/amazon/openmpi

COPY "${SCRIPT_PATH}/cudaq_wheel/wheelhouse/cuda_quantum_cu12-0.0.0-cp310-cp310-manylinux_2_28_x86_64.whl" .
RUN python3 -m pip install cuda_quantum_cu12-0.0.0-cp310-cp310-manylinux_2_28_x86_64.whl
RUN bash "${CUDAQ_PATH}/distributed_interfaces/activate_custom_mpi.sh"

# install additional python dependencies
RUN python3 -m pip install --no-cache --upgrade -r requirements.txt

# Setup our entry point
COPY "${SCRIPT_PATH}/braket_container.py" /opt/ml/code/braket_container.py
ENV SAGEMAKER_PROGRAM=braket_container.py
