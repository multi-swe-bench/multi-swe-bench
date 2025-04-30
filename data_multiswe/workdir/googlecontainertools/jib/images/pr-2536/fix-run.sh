#!/bin/bash
set -e

cd /home/jib
git apply /home/test.patch /home/fix.patch
./gradlew clean test --continue

