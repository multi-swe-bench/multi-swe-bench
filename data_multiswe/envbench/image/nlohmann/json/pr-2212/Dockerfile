FROM gcc:7
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
RUN git checkout 8575fdf9ad41844692b18fb9db4d28fea4e9282a
RUN bash /home/check_git_changes.sh

