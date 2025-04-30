#!/bin/bash
set -e

cd /home/jackson-core
git apply --whitespace=nowarn /home/test.patch
mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -Dtest=com.fasterxml.jackson.failing.PerfBigDecimalToInteger968 -DfailIfNoTests=false -am

