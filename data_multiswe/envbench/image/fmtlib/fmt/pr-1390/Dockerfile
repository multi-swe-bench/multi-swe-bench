FROM gcc:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/fmtlib/fmt.git /home/fmt

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/fmt
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout d6eede9e085f0b36edcf0a2f6dff5f7875181019
RUN bash /home/check_git_changes.sh

