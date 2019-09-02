FROM python:3

RUN \
    git clone git://github.com/Ragnaruk/ExternalGrader.git && \
    pip install -r ./ExternalGrader/requirements.txt

CMD [ "python", "./ExternalGrader/external_grader/main.py" ]