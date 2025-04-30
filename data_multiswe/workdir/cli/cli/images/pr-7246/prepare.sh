#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 82662685e3cf3e93fd0c5c81b6680c6a06491f1d
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

