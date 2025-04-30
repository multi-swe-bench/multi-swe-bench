FROM ubuntu:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/iamkun/dayjs.git /home/dayjs

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/dayjs
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 72cdb20552dd5af6c2295bf52075ba19cceb000f
RUN bash /home/check_git_changes.sh

