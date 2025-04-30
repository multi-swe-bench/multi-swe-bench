#!/bin/bash
set -e

cd /home/jackson-core
git apply --whitespace=nowarn /home/test.patch
mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false

