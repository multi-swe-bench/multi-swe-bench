#!/bin/bash
set -e

cd /home/gson
git apply --whitespace=nowarn /home/test.patch /home/fix.patch
mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false

