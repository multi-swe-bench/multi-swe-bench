FROM ubuntu:22.04
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/apache/dubbo.git /home/dubbo

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/dubbo
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout ddd1786578438c68f1f6214bcab600a299245d7d
RUN bash /home/check_git_changes.sh

