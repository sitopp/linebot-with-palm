FROM python:3.8-slim-buster
ARG dir=/workdir
WORKDIR $dir
COPY . .
RUN pip install -r ./requirements.txt
VOLUME $dir
CMD [ "python", "./opt/main.py" ]
