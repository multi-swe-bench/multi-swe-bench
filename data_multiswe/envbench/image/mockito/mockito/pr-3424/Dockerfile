FROM ubuntu:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/mockito/mockito.git /home/mockito

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/mockito
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 87e4a4fa85c84cbd09420c2c8e73bab3627708a7
RUN bash /home/check_git_changes.sh

