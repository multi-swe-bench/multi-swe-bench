FROM node:18
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/mui/material-ui.git /home/material-ui

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/material-ui
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout fa62bf35e109ede215cb8cbae66ba4d6a30fef60
RUN bash /home/check_git_changes.sh

