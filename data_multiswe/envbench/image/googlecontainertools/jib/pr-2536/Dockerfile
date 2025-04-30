FROM ubuntu:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/googlecontainertools/jib.git /home/jib

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/jib
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout cb78087f2738ab214af739b915e7279b4fcf6aa1
RUN bash /home/check_git_changes.sh

