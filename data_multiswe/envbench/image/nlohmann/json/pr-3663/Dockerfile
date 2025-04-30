FROM gcc:12
ENV http_proxy=http://sys-proxy-rd-relay.byted.org:8118
ENV https_proxy=http://sys-proxy-rd-relay.byted.org:8118
RUN apt-get update && apt-get install -y git


WORKDIR /home/
RUN git clone https://github.com/nlohmann/json.git /home/json
RUN cd /home/ && git clone https://github.com/nlohmann/json_test_data.git

COPY run.sh /home/
COPY check_git_changes.sh /home/

WORKDIR /home/json
RUN git reset --hard
RUN bash /home/check_git_changes.sh
RUN git checkout 7b6cf5918bc9a4b85d1e3fb9ff65348d6dce5d10
RUN bash /home/check_git_changes.sh

