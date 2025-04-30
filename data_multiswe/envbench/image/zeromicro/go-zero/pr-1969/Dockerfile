FROM golang:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/zeromicro/go-zero.git /home/go-zero

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/go-zero
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout af05219b70c5e18542ebb499b18a1dff6ffacc6d
RUN bash /home/check_git_changes.sh

