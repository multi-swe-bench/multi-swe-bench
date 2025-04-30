FROM rust:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/sharkdp/fd.git /home/fd

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/fd
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 2bab4a22494e3f10da0b708da7a1eebaa483b727
RUN bash /home/check_git_changes.sh

