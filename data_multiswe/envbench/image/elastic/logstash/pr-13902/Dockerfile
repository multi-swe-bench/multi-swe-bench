FROM ubuntu:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/elastic/logstash.git /home/logstash

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/logstash
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 32675c1a88bd3393e3f8d6d9275217d2f3891e66
RUN bash /home/check_git_changes.sh

