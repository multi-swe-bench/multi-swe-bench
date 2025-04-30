#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout cb06812d192e0abc2093351a1d709b21cb06928e
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

