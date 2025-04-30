FROM ubuntu:22.04
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/jqlang/jq.git /home/jq

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/jq
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout c077b95ba2dcaafee39e302cc086bf99fa9248d0
RUN bash /home/check_git_changes.sh

