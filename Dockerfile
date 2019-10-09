FROM python:3

RUN \
    apt -y update && \
    apt -y upgrade && \
    apt -y install ffmpeg

COPY . /ExternalGrader

RUN \
    pip install --no-cache-dir -r /ExternalGrader/requirements.txt && \
    ln -sf /dev/stdout /ExternalGrader/grader.log

ENV PYTHONPATH /ExternalGrader/

CMD [ "python", "/ExternalGrader/external_grader/" ]