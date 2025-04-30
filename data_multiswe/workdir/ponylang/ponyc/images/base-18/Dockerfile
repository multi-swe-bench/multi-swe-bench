FROM ubuntu:18.04



WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN apt update && apt install -y git llvm clang build-essential wget tar python3 python3-dev python3-pip
RUN wget https://cmake.org/files/v3.16/cmake-3.16.3-Linux-x86_64.tar.gz &&     tar -zxvf cmake-3.16.3-Linux-x86_64.tar.gz &&     mv cmake-3.16.3-Linux-x86_64 /opt/cmake &&     ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake &&     rm cmake-3.16.3-Linux-x86_64.tar.gz
    
RUN git clone https://github.com/ponylang/ponyc.git /home/ponyc



