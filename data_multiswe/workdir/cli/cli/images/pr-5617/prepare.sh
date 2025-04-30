#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 06fb78aa26eb0af2cb7c9e6a18f5b6e5ca222696
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

