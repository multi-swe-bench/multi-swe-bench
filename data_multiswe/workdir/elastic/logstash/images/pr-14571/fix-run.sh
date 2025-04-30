#!/bin/bash
set -e

cd /home/logstash
git apply /home/test.patch /home/fix.patch
./gradlew clean test --continue

