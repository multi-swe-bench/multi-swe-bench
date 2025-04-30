#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e14f0d79bd3a6d7f839bc547bf148f228c9a44d9
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

