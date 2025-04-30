FROM golang:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/grpc/grpc-go.git /home/grpc-go

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/grpc-go
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout b88d2d74656f2b9833cc78c088ebf899d2189230
RUN bash /home/check_git_changes.sh

