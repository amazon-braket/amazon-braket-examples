#!/usr/bin/env bash

# This script shows how to build the Docker image and push it to ECR to be ready for use
# by SageMaker.

# The argument to this script is the image name. This will be used as the image on the local
# machine and combined with the account and region to form the repository name for ECR.

image=$1
region=$2

if [ "$image" == "" ]
then
    echo "Usage: $0 <image-name>"
    exit 1
fi

# Get the account number associated with the current IAM credentials
account=$(aws sts get-caller-identity --query Account --output text)

if [ $? -ne 0 ]
then
    exit 255
fi

# Get the region defined in the current configuration (default to us-west-2 if none defined)
# region=$(aws configure get region)
region=${region:-us-west-2}


fullname="${account}.dkr.ecr.${region}.amazonaws.com/${image}:latest"

# If the repository doesn't exist in ECR, create it.
aws ecr describe-repositories --repository-names "${image}" > /dev/null 2>&1

if [ $? -ne 0 ]
then
    aws ecr create-repository --repository-name "${image}" > /dev/null
fi

# Get the login command from ECR and execute it directly
get_login_password="aws ecr get-login-password --region ${region}"
login_password=$($get_login_password)
docker login -u AWS -p ${login_password} ${account}.dkr.ecr.${region}.amazonaws.com

# Login to pull from Braket pre-built container image
docker login -u AWS -p $(aws ecr get-login-password --region us-west-2) 292282985366.dkr.ecr.us-west-2.amazonaws.com

# Build the docker image locally with the image name and then push it to ECR
# with the full name.
script_dir=$(dirname "$0")

docker build --build-arg SCRIPT_PATH="$script_dir" \
-t ${image} -f "${script_dir}/Dockerfile" . --platform linux/amd64 --progress=plain \

docker tag ${image} ${fullname}

docker push ${fullname}
