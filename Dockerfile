FROM python:3.8

RUN pip3.8 install boto3
COPY warmup.py /warmup.py

ENTRYPOINT ["/warmup.py"]
