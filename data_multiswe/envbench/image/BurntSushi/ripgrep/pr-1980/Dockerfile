FROM rust:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/BurntSushi/ripgrep.git /home/ripgrep

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/ripgrep
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 9b01a8f9ae53ebcd05c27ec21843758c2c1e823f
RUN bash /home/check_git_changes.sh

