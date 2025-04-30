FROM ubuntu:22.04



WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN apt-get update &&     apt-get install -y automake autoconf libtool git make gcc g++     && apt-get clean

RUN apt-get install -y crossbuild-essential-amd64

RUN git clone https://github.com/jqlang/jq.git /home/jq



