#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 3b9f9a8f5985bdb0d538314cd1e8773765f3e37b
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

