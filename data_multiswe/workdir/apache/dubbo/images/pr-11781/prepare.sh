#!/bin/bash
set -e

cd /home/dubbo
git reset --hard
bash /home/check_git_changes.sh
git checkout d0a1bd014331483c19208b831c4f6b488654a508
bash /home/check_git_changes.sh

mvn clean test -Dsurefire.useFile=false -Dmaven.test.skip=false -DfailIfNoTests=false || true
