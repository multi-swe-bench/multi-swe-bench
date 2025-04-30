FROM gcc:11



WORKDIR /home/

RUN git clone https://github.com/simdjson/simdjson.git /home/simdjson

RUN apt-get update && apt-get install -y libbrotli-dev libcurl4-openssl-dev
RUN apt-get install -y clang build-essential cmake pkg-config



