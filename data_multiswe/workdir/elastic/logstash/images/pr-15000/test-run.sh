#!/bin/bash
set -e

cd /home/logstash
git apply /home/test.patch
./gradlew clean test --continue

