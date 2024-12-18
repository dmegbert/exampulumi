FROM public.ecr.aws/lambda/python:3.12-arm64

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Copy function code
WORKDIR ${LAMBDA_TASK_ROOT}
COPY alembic.ini .
ADD alembic alembic
ADD src src
COPY lambda_handler.py .

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["lambda_handler.handle_event"]
