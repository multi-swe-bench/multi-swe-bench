FROM rust:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/tokio-rs/tokio.git /home/tokio

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/tokio
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout fb7dec0e952d0d796b98650998c44a21d6775564
RUN bash /home/check_git_changes.sh

