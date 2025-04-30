#!/bin/bash
set -e

cd /home/jackson-core
mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false
