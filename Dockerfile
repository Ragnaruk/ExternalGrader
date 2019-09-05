FROM python:3

COPY . /ExternalGrader

RUN \
    apt -y update && \
    apt -y upgrade && \
    apt -y install ffmpeg && \
    pip install --no-cache-dir -r /ExternalGrader/requirements.txt && \
    ln -sf /dev/stdout /grader.log

ENV PYTHONPATH /ExternalGrader/

CMD [ "python", "/ExternalGrader/external_grader/" ]