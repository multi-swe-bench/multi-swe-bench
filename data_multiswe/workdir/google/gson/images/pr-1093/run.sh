#!/bin/bash
set -e

cd /home/gson
mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false
