FROM ubuntu:16.04



WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN apt update && apt install -y git clang build-essential cmake

RUN git clone https://github.com/ponylang/ponyc.git /home/ponyc



