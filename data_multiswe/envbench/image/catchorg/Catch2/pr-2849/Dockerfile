FROM gcc:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/catchorg/Catch2.git /home/Catch2

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/Catch2
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 7ce35799767de7b9c6ba836c72e479c5f70219a3
RUN bash /home/check_git_changes.sh

