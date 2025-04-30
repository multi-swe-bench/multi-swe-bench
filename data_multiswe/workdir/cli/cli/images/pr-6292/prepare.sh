#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 0ecd424901427fa96e4b322290d480b5f1350baa
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

