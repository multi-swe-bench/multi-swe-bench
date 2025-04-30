#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7c2e5fd5957a0db0229a7a20352bfe6c91462de3
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

