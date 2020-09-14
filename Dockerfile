FROM amazon/aws-cli

COPY warmup.py /warmup.py

ENTRYPOINT ["/warmup.py"]