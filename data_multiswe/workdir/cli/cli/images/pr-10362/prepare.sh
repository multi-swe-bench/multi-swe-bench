#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 0a05012ca6d6afc95f4d4ab63be0ceb0d99dfe0c
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

