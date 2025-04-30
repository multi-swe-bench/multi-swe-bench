FROM ubuntu:22.04
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/google/gson.git /home/gson

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/gson
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 3f4ac29f9112799a7374a99b18acabd0232ff075
RUN bash /home/check_git_changes.sh

