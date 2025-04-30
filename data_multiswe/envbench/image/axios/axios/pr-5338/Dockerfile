FROM ubuntu:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/axios/axios.git /home/axios

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/axios
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 7fbfbbeff69904cd64e8ac62da8969a1e633ee23
RUN bash /home/check_git_changes.sh

