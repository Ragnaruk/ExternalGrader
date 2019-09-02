FROM python:3

ARG VERSION=5

RUN \
    git clone git://github.com/Ragnaruk/ExternalGrader.git && \
    pip install --no-cache-dir -r /ExternalGrader/requirements.txt && \
    ln -sf /dev/stdout /grader.log

ENV PYTHONPATH /ExternalGrader/

CMD [ "python", "./ExternalGrader/external_grader/main.py" ]