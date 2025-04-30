FROM node:20
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/vuejs/core.git /home/core

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/core
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout fc772dbf7398e8ce961025556594b4a7d3f64871
RUN bash /home/check_git_changes.sh

