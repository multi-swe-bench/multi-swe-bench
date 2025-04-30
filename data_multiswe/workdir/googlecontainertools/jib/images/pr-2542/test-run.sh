#!/bin/bash
set -e

cd /home/jib
git apply /home/test.patch
./gradlew clean test --continue

