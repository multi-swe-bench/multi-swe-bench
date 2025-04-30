#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e356c69a6f0125cfaac782c35acf77314f18908d
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

