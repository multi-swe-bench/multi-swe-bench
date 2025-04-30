FROM ubuntu:22.04



ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
WORKDIR /home/
RUN apt-get update && apt-get install -y git openjdk-11-jdk
RUN apt-get install -y maven

RUN git clone https://github.com/google/gson.git /home/gson



