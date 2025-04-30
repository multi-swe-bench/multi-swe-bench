#!/bin/bash
set -e

cd /home/logstash
./gradlew clean test --continue

