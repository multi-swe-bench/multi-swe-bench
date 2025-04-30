FROM rust:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/rayon-rs/rayon.git /home/rayon

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/rayon
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout ebcb09b1dc53211c6b5abdf4dc5b40e4bcd0a965
RUN bash /home/check_git_changes.sh

