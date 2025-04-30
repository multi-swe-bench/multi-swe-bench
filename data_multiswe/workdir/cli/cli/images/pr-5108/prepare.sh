#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout b77c37df0f17b596d07569e455d454b64e3bc75e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

