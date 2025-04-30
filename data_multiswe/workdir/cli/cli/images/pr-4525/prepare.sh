#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout a9d397be6941255f4f027c0986c58a7421086e94
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

