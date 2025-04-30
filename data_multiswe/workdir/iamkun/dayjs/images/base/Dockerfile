FROM ubuntu:latest



WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN apt update && apt install -y git nodejs npm && npm install -g codecov

RUN git clone https://github.com/iamkun/dayjs.git /home/dayjs



