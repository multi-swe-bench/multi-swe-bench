FROM node:20
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/Kong/insomnia.git /home/insomnia

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/insomnia
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 44642a49e9a104a53964b3b2b9c589910d391236
RUN bash /home/check_git_changes.sh

