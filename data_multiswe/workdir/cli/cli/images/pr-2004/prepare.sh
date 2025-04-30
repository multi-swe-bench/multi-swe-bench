#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 7fecaaa8e28aac3132c27699426df816fed23371
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

