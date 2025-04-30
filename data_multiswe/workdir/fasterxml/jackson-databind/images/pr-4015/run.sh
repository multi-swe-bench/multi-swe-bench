#!/bin/bash
set -e

cd /home/jackson-databind
mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false
