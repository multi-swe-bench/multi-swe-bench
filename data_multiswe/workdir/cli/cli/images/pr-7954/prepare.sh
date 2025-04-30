#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 60f2da2d1f22201b4f624fced9c10731b7c51acb
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

