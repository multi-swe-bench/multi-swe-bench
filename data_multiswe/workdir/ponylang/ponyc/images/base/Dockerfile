FROM ubuntu:22.04



WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN apt update && apt install -y git clang build-essential cmake pkg-config make gcc pkg-config libjemalloc-dev automake libtool libssl-dev libpsl-dev

RUN git clone https://github.com/ponylang/ponyc.git /home/ponyc





