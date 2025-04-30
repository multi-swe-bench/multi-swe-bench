#!/bin/bash
set -e

cd /home/dubbo
mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -DfailIfNoTests=false
