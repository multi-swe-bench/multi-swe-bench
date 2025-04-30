FROM ubuntu:20.04
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/facebook/zstd.git /home/zstd

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/zstd
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout e26126cacaa9ac6f1db4021ac3d32f4ac8387c50
RUN bash /home/check_git_changes.sh

