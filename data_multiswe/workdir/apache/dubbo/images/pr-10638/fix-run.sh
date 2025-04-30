#!/bin/bash
set -e

cd /home/dubbo
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -DfailIfNoTests=false

