FROM public.ecr.aws/lambda/python:3.8

RUN pip install fastapi "uvicorn[standard]" mangum

ADD main.py ${LAMBDA_TASK_ROOT}

CMD ["main.handler"]