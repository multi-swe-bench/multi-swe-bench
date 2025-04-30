#!/bin/bash
set -e

cd /home/fastjson2
git apply /home/test.patch /home/fix.patch
./mvnw -V --no-transfer-progress -Pgen-javadoc -Pgen-dokka clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -DfailIfNoTests=false

