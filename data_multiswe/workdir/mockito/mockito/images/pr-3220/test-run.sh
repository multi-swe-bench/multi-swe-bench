#!/bin/bash
set -e

cd /home/mockito
git apply /home/test.patch
./gradlew test

