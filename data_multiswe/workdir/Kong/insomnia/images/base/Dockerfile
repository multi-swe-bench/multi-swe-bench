FROM node:20



WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN apt update && apt install -y git 

RUN git clone https://github.com/Kong/insomnia.git /home/insomnia



