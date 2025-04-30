FROM gcc:latest



WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN apt-get update && apt-get install -y libbrotli-dev libcurl4-openssl-dev
RUN apt-get install -y clang build-essential

RUN git clone https://github.com/yhirose/cpp-httplib.git /home/cpp-httplib



