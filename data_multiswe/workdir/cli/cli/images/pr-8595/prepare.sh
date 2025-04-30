#!/bin/bash
set -e

cd /home/cli
git reset --hard
bash /home/check_git_changes.sh
git checkout 8948ee8c3beaf432676061aaaf481d2f41039483
bash /home/check_git_changes.sh

go test -v -count=1 ./... || true

