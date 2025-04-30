#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout fc2aec380dd94c6d4eba57aaf075830ccb311f30
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

