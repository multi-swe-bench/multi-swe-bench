#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 06c06c87dc02e5a7b50d9771ae4178bd10317e8d
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

