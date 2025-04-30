#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 82bd7b97cf0a3919c616c737136e3f3cee0c9bc9
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

