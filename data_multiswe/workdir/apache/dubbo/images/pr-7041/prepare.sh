#!/bin/bash
set -e

cd /home/dubbo
git reset --hard
bash /home/check_git_changes.sh
git checkout e84cdc217a93f4628415ea0a7d8a9d0090e2c940
bash /home/check_git_changes.sh

mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -DfailIfNoTests=false || true
