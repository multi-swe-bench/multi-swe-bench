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
RUN git checkout 3f6eff55a4dc6d6a76efb2f23a971f15ee524ddd
RUN bash /home/check_git_changes.sh

