FROM python:3.11.4
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_ROOT_USER_ACTION=ignore

RUN apt-get update && \
  apt-get install -y \
  g++ \
  gcc \
  make \
  cmake \
  unzip \
  libcurl4-openssl-dev

RUN mkdir backend
WORKDIR backend
COPY requirements.txt ./
RUN python3.11 -m pip install --upgrade pip
RUN python3.11 -m pip install -r requirements.txt --use-pep517

ENV PYTHONPATH=$PYTHONPATH:./src

ADD alembic alembic
COPY alembic.ini ./
ADD src src
