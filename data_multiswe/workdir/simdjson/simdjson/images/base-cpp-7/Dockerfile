FROM gcc:7



WORKDIR /home/

RUN git clone https://github.com/simdjson/simdjson.git /home/simdjson

RUN apt-get update &&     apt-get install -y     build-essential     pkg-config     wget     tar &&     wget https://cmake.org/files/v3.14/cmake-3.14.0-Linux-x86_64.tar.gz &&     tar -zxvf cmake-3.14.0-Linux-x86_64.tar.gz &&     mv cmake-3.14.0-Linux-x86_64 /opt/cmake &&     ln -s /opt/cmake/bin/cmake /usr/local/bin/cmake &&     rm cmake-3.14.0-Linux-x86_64.tar.gz
RUN apt-get install -y cmake



