FROM golang:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/cli/cli.git /home/cli

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/cli
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout de07febc26e19000f8c9e821207f3bc34a3c8038
RUN bash /home/check_git_changes.sh

