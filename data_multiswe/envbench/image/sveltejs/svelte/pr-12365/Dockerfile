FROM ubuntu:latest
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/sveltejs/svelte.git /home/svelte

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/svelte
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 6ac1ae8a12552f8a4444f3b1bc938d2989c7726a
RUN bash /home/check_git_changes.sh

