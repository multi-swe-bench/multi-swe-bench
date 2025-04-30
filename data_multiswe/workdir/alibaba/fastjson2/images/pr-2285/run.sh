#!/bin/bash
set -e

cd /home/fastjson2
./mvnw -V --no-transfer-progress -Pgen-javadoc -Pgen-dokka clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -DfailIfNoTests=false

