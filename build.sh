#!/bin/bash

PYTHON_VERSION=${PYTHON_VERSION:-3.8}
PROJECT_NAME=nomad-watcher
BUILD_PREFIX=./build

AWS_REGION=${AWS_REGION:-us-east-1}

[ ! -d ${BUILD_PREFIX} ] && mkdir ${BUILD_PREFIX}

# Use docker to install packages into a target directory
docker run \
  --rm -ti \
  -v ${PWD}:/opt \
  -w /opt \
  python:${PYTHON_VERSION}-alpine \
  /bin/sh -c \
    "pip install -r requirements.txt -t ${BUILD_PREFIX}"

# Add relevant code to build directory
cp -r \
  ./lambda_function.py \
  ./nomad_notifications \
  ${BUILD_PREFIX}

rm -f ${PROJECT_NAME}.zip
find ./ -type f -name "*.pyc" -exec rm -f \{} \;
find ./ -type d -name "__pycache__" -exec rm -rf \{} \;

# Build zip package to be deployed to AWS
pushd ${BUILD_PREFIX} && zip -r ../${PROJECT_NAME}.zip ./ -x "*.pyc" "*.swa" "*.swp" && popd

aws lambda update-function-code \
  --function-name ${PROJECT_NAME} \
  --zip-file fileb://${PROJECT_NAME}.zip \
  --region ${AWS_REGION}
