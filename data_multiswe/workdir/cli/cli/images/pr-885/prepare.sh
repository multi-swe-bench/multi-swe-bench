#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout aac9947a51b8133807c07830a079137473e86ad4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

