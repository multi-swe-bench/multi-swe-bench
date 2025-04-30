FROM ubuntu:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/expressjs/express.git /home/express

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/express
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout dc538f6e810bd462c98ee7e6aae24c64d4b1da93
RUN bash /home/check_git_changes.sh

