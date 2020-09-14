FROM python:3.8

COPY warmup.py /warmup.py

ENTRYPOINT ["/warmup.py"]