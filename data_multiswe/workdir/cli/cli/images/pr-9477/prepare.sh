#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 1886fb46aba416e01e5b6ab43fc8e744342d8fb1
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

