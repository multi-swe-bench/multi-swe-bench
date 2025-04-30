FROM rust:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/tokio-rs/tracing.git /home/tracing

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/tracing
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 63015eb8d9c5261d9a384e11dc84552f23a5209c
RUN bash /home/check_git_changes.sh

