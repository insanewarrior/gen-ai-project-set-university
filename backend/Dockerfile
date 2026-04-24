FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.12 AS builder

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -t /opt/python

FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.12

COPY --from=builder /opt/python ${LAMBDA_TASK_ROOT}
COPY . ${LAMBDA_TASK_ROOT}

CMD ["main.handler"]
