FROM ubuntu:20.04
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/alibaba/fastjson2.git /home/fastjson2

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/fastjson2
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 12b40c7ba3e7c30e35977195770c80beb34715c5
RUN bash /home/check_git_changes.sh

