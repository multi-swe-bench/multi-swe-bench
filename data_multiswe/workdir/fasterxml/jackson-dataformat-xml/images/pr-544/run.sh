#!/bin/bash
set -e

cd /home/jackson-dataformat-xml
mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false
