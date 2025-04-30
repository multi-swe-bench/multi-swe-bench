#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 537dcb27398bd193a094d5fcd3aa9bc67a546328
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

