FROM rust:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/clap-rs/clap.git /home/clap

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/clap
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 9962393c20f2d1521aefdcf2562bef1380b4ccbe
RUN bash /home/check_git_changes.sh

