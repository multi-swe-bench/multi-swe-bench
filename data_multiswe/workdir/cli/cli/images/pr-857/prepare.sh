#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout e93b18a9af8bf745d98968834d82f14a98dd09ff
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

