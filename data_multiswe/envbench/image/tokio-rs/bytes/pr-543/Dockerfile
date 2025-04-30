FROM rust:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/tokio-rs/bytes.git /home/bytes

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/bytes
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout f514bd38dac85695e9053d990b251643e9e4ef92
RUN bash /home/check_git_changes.sh

