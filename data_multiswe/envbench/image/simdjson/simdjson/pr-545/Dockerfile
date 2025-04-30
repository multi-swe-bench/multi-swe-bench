FROM gcc:7
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/simdjson/simdjson.git /home/simdjson

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/simdjson
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout e4e89fe27a37a1abf70387d07adfb3b1b9f115ef
RUN bash /home/check_git_changes.sh

