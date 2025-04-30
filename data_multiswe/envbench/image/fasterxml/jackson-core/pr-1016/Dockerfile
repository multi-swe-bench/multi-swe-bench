FROM ubuntu:22.04
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/fasterxml/jackson-core.git /home/jackson-core

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/jackson-core
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 315ac5ad2ad5228129a3df50623570d9bc2d7045
RUN bash /home/check_git_changes.sh

