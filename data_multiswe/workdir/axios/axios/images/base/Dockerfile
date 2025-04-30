FROM ubuntu:latest



WORKDIR /home/
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN apt update && apt install -y git curl &&     curl -fsSL https://deb.nodesource.com/setup_20.x | bash - &&     apt install -y nodejs
     
RUN git clone https://github.com/axios/axios.git /home/axios



