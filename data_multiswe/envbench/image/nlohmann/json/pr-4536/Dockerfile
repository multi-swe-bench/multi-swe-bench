FROM gcc:latest
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
RUN git checkout e6cafa573aac6ed9227f752a5371c0b3f436307d
RUN bash /home/check_git_changes.sh

