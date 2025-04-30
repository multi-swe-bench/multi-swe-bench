FROM ubuntu:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/anuraghazra/github-readme-stats.git /home/github-readme-stats

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/github-readme-stats
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout fef8bc3a4a4ddb12a5c779e7cae18438231845a7
RUN bash /home/check_git_changes.sh

