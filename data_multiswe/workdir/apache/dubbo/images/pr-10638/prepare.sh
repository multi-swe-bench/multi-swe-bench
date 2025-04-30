#!/bin/bash
set -e

cd /home/dubbo
git reset --hard
bash /home/check_git_changes.sh
git checkout ddd1786578438c68f1f6214bcab600a299245d7d
bash /home/check_git_changes.sh

mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -DfailIfNoTests=false || true
