FROM rust:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/sharkdp/bat.git /home/bat

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/bat
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout e1a3fc5529d55abc73aa5fb18368d22f9b9bb71c
RUN bash /home/check_git_changes.sh

