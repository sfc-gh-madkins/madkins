FROM ubuntu:22.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa

RUN  apt-get install python3-pip -y

RUN pip install 'feast[snowflake,redis]'

RUN ln -s /usr/bin/python3 /usr/bin/python