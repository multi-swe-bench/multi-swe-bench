#!/bin/bash
set -e

cd /home/mockito
git apply /home/test.patch /home/fix.patch
./gradlew test

