FROM gcc:11
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
RUN git checkout 47a62db55936e29e1966a26a9aadb5f28237ae37
RUN bash /home/check_git_changes.sh

