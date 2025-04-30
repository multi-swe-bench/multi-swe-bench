#!/bin/bash
set -e

cd /home/jackson-databind
git apply --whitespace=nowarn /home/test.patch
mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -Dtest=com.fasterxml.jackson.databind.deser.creators.JsonCreatorModeForEnum3566 -DfailIfNoTests=false -am

