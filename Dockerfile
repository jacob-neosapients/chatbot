FROM public.ecr.aws/lambda/python:3.11

# Install build dependencies for numpy and other packages
RUN yum install -y gcc gcc-c++ make

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r requirements.txt

# Copy model files from your local rm_guardrail_model/ directory into the container
# This packages ~2GB of model files into the Docker image
COPY rm_guardrail_model/ ${LAMBDA_TASK_ROOT}/rm_guardrail_model/

# Copy Flask app
COPY app.py ${LAMBDA_TASK_ROOT}/

# Add Mangum for Lambda handler (converts Flask to Lambda-compatible)
RUN pip install mangum

# Create handler wrapper
RUN echo "from mangum import Mangum\nfrom app import app\nhandler = Mangum(app)" > ${LAMBDA_TASK_ROOT}/lambda_handler.py

CMD ["lambda_handler.handler"]
