FROM gcc:latest



WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN apt-get update && apt-get install -y cmake

RUN git clone https://github.com/fmtlib/fmt.git /home/fmt



