FROM rust:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/serde-rs/serde.git /home/serde

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/serde
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 5b24f88e73caa9c607527b5b4696fc34263cd238
RUN bash /home/check_git_changes.sh

