#!/bin/bash
set -e

cd /home/jib
./gradlew clean test --continue

