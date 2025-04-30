#!/bin/bash
set -e

cd /home/gson
git reset --hard
bash /home/check_git_changes.sh
git checkout e614e71ee43ca7bc1cb466bd1eaf4d85499900d9
bash /home/check_git_changes.sh

mvn clean test -Dmaven.test.skip=false -DfailIfNoTests=false || true
