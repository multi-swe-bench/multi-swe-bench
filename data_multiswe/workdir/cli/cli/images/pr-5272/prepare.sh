#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 65d90aa24de1dcbd0b8ab893ddc0828edf7e05b4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

