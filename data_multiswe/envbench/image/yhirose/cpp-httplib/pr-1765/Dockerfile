FROM gcc:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/yhirose/cpp-httplib.git /home/cpp-httplib

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/cpp-httplib
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 44b3fe6277398f424f1844295b7ae46ba5a1a35f
RUN bash /home/check_git_changes.sh

