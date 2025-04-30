#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 6d11395c083cbba795b955075ddbb92c289fd1df
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

