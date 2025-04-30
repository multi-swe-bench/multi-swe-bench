FROM rust:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/nushell/nushell.git /home/nushell

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/nushell
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 399319476aa4decd7cced93488180d96e56bad64
RUN bash /home/check_git_changes.sh

