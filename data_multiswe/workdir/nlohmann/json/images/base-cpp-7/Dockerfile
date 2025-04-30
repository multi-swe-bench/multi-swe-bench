FROM gcc:7



WORKDIR /home/

RUN git clone https://github.com/nlohmann/json.git /home/json

RUN apt-get update && apt-get install -y libbrotli-dev libcurl4-openssl-dev
RUN apt-get install -y clang build-essential cmake
RUN cd /home/ && git clone https://github.com/nlohmann/json_test_data.git



