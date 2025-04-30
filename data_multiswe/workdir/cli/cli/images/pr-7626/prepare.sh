#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout baba8949973244a53f6a172a03afa84a7a0ccfc4
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

