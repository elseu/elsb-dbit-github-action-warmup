FROM python:3.11

RUN pip3.11 install boto3
COPY warmup.py /warmup.py

ENTRYPOINT ["/warmup.py"]
