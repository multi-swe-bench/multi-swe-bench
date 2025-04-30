#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout ae99ad4fbe844dc100797c13d7732a38b5ced421
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

