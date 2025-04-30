#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 104d7655d7b30b3f70679e82bec251a73e1d9d02
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

