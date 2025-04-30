FROM ubuntu:22.04
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/fasterxml/jackson-databind.git /home/jackson-databind

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/jackson-databind
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout bed90645e269d30b0b94d446f821a3a0f45ce07b
RUN bash /home/check_git_changes.sh

