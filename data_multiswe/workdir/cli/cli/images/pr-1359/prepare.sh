#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 53ff3842e7a720c440ec7097e71385b071e6cfee
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

