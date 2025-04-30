FROM node:18
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/darkreader/darkreader.git /home/darkreader

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/darkreader
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout a787eb511f45159c8869d30e5a6ba1f91cb67709
RUN bash /home/check_git_changes.sh

