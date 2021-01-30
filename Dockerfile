FROM python:3.9.1-alpine3.12

RUN apk add --no-cache g++
RUN apk add --no-cache make
RUN apk add --no-cache zlib-dev
RUN apk add --no-cache jpeg-dev
RUN pip install numpy==1.19.5
RUN pip install matplotlib==3.3.4

WORKDIR /app
COPY ./simulation.py /app/simulation.py

ENTRYPOINT [ "python", "simulation.py" ]
