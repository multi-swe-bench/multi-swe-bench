FROM ubuntu:22.04
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/fasterxml/jackson-dataformat-xml.git /home/jackson-dataformat-xml

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/jackson-dataformat-xml
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout b782f4b9559ece1b6178cbeafa8acffb0ab9d0f0
RUN bash /home/check_git_changes.sh

