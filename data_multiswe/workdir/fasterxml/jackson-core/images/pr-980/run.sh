#!/bin/bash
set -e

cd /home/jackson-core
mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -Dtest=com.fasterxml.jackson.failing.PerfBigDecimalToInteger968 -DfailIfNoTests=false -am

