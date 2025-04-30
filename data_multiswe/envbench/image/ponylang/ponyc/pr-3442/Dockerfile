FROM ubuntu:16.04
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/ponylang/ponyc.git /home/ponyc

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/ponyc
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 764110c805d8020f5202c60ffed2b2570caf792a
RUN bash /home/check_git_changes.sh

